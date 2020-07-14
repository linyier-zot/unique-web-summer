package mr

import (
	"log"
	"net"
	"net/http"
	"net/rpc"
	"os"
	"sync"
	"time"
)

type job struct {
	state   int
	Thetime time.Time
	file    string
}

type Master struct {
	mutex sync.Mutex //锁

	MapNum    int
	ReduceNum int

	Poolmap           []job
	MapOver           bool
	Poolreduce        []job
	RedeuceOver       bool
	Intermediatefiles []string
}

/* Askforjob worker请求job时rpc调用此方法 */
func (m *Master) Askforjob(args *Forjobargs, reply *Forjobreply) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	now := time.Now()
	for k := 0; k < m.MapNum; k++ {
		if m.Poolmap[k].state != WAIT {
			continue
		}
		// fmt.Println("增加前", m.Poolmap[k].Thetime)
		temp := m.Poolmap[k].Thetime
		temp = temp.Add(time.Duration(10) * time.Second)
		// fmt.Println("增加后", m.Poolmap[k].Thetime)
		if temp.Before(now) { //超时了
			// fmt.Println(k, "超时了")
			m.Poolmap[k].state = UNALLOCATE
		}
	}
	for k := 0; k < m.ReduceNum; k++ {
		if m.Poolreduce[k].state != WAIT {
			continue
		}
		temp := m.Poolreduce[k].Thetime
		temp.Add(time.Duration(10) * time.Second)
		if !temp.After(now) { //超时了
			m.Poolreduce[k].state = UNALLOCATE
		}
	}

	// fmt.Println("askfor be called")
	if m.MapOver && m.RedeuceOver {
		reply.JobType = EXIT //完工了
		return nil
	}

	if !m.MapOver {
		reply.JobType = MAP
		var i int
		for i = 0; i < m.MapNum; i++ {
			if m.Poolmap[i].state == UNALLOCATE {
				break
			}
		}
		// fmt.Println(i)
		if i == m.MapNum { //没有未分配的任务，进入待机状态
			reply.JobType = AWAIT
			return nil
		}
		m.Poolmap[i].state = WAIT
		m.Poolmap[i].Thetime = time.Now()
		// fmt.Println(m.Poolmap[i])
		reply.File = m.Poolmap[i].file
		reply.NReduce = m.ReduceNum
		reply.TheNum = i
		reply.Worktime = m.Poolmap[i].Thetime
		return nil

	}
	if !m.RedeuceOver {
		reply.JobType = REDUCE
		var i int
		for i = 0; i < m.ReduceNum; i++ {
			if m.Poolreduce[i].state == UNALLOCATE {
				break
			}
		}
		if i == m.ReduceNum {
			reply.JobType = AWAIT
			return nil
		}
		m.Poolreduce[i].state = WAIT
		m.Poolreduce[i].Thetime = time.Now()
		reply.TheNum = i
		reply.Intermediatefiles = m.Intermediatefiles
		reply.Worktime = m.Poolreduce[i].Thetime
		return nil
	}

	return nil
}

func (m *Master) HandinMap(args *Forjobargs, reply *Forjobreply) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	j := args.Num

	t := args.Mytime //工作池中时间和自己之前拿到的时间不等，说明已被认为自己down掉了
	if !t.Equal(m.Poolmap[j].Thetime) {
		// fmt.Println("时间不等，退出")
		// fmt.Println("我的时间", t)
		// fmt.Println("工作池时间", m.Poolmap[j].Thetime)
		return nil
	}
	// fmt.Println("handinMap be called")

	temp := args.Tempfiles
	need := args.Filenames

	for i := 0; i < len(temp); i++ {
		os.Rename(temp[i], need[i])
	}
	m.Poolmap[j].state = COMPLETED
	m.Intermediatefiles = append(m.Intermediatefiles, need...)
	/* 检测 */
	var k int
	for k = 0; k < m.MapNum; k++ {
		if m.Poolmap[k].state != COMPLETED {
			break
		}
	}
	if k == m.MapNum {
		m.MapOver = true
	}
	for k = 0; k < m.ReduceNum; k++ {
		if m.Poolreduce[k].state != COMPLETED {
			break
		}
	}
	if k == m.ReduceNum {
		m.RedeuceOver = true
	}
	/**/

	return nil
}

func (m *Master) HandinReduce(args *Forjobargs, reply *Forjobreply) error {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	// fmt.Println("handinReduce be called")

	j := args.Num

	m.Poolreduce[j].state = COMPLETED
	/* 检测 */
	var k int
	for k = 0; k < m.MapNum; k++ {
		if m.Poolmap[k].state != COMPLETED {
			break
		}
	}
	if k == m.MapNum {
		m.MapOver = true
	}
	for k = 0; k < m.ReduceNum; k++ {
		if m.Poolreduce[k].state != COMPLETED {
			break
		}
	}
	if k == m.ReduceNum {
		m.RedeuceOver = true
	}
	/**/

	return nil
}

func (m *Master) server() {
	rpc.Register(m)
	rpc.HandleHTTP()
	//l, e := net.Listen("tcp", ":1234")
	sockname := masterSock()
	os.Remove(sockname)
	l, e := net.Listen("unix", sockname)
	if e != nil {
		log.Fatal("listen error:", e)
	}
	go http.Serve(l, nil)
}

func (m *Master) Done() bool {
	m.mutex.Lock()
	defer m.mutex.Unlock()

	return m.MapOver && m.RedeuceOver
}

func (m *Master) init(files []string, nReduce int) {
	m.MapNum = len(files)
	m.ReduceNum = nReduce
	m.Poolmap = make([]job, m.MapNum)
	m.MapOver = false
	m.Poolreduce = make([]job, nReduce)
	m.RedeuceOver = false

	for i := 0; i < m.MapNum; i++ {
		m.Poolmap[i].state = UNALLOCATE
		m.Poolmap[i].file = files[i]
	}
	for i := 0; i < nReduce; i++ {
		m.Poolreduce[i].state = UNALLOCATE
	}
}

func MakeMaster(files []string, nReduce int) *Master {
	m := Master{}
	m.init(files, nReduce)

	// fmt.Println(m.Poolmap)
	m.server()
	return &m
}
