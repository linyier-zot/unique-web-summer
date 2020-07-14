package mr

import (
	"encoding/json"
	"fmt"
	"hash/fnv"
	"io/ioutil"
	"log"
	"net/rpc"
	"os"
	"sort"
	"strconv"
	"time"
)

type KeyValue struct {
	Key   string
	Value string
}

// for sorting by key.
type ByKey []KeyValue

func (a ByKey) Len() int           { return len(a) }
func (a ByKey) Swap(i, j int)      { a[i], a[j] = a[j], a[i] }
func (a ByKey) Less(i, j int) bool { return a[i].Key < a[j].Key }

//
// Map functions return a slice of KeyValue.
//
//
// use ihash(key) % NReduce to choose the reduce
// task number for each KeyValue emitted by Map.
//
func ihash(key string) int {
	h := fnv.New32a()
	h.Write([]byte(key))
	return int(h.Sum32() & 0x7fffffff)
}

//
func Worker(mapf func(string, string) []KeyValue,
	reducef func(string, []string) string) {

	// Your worker implementation here.
	for {
		reply, status := Calljob()
		// fmt.Println(123)
		// fmt.Println(reply)
		if status == false {
			return
		}
		switch reply.JobType {
		case EXIT:
			return
		case MAP:
			DoMap(reply, mapf)
		case REDUCE:
			DoReduce(reply, reducef)
		case AWAIT:
			// fmt.Println("AWAIT,return")
			time.Sleep(time.Second)
			// return
		}

	}

}

func DoMap(HHH Forjobreply, mapf func(string, string) []KeyValue) {
	// fmt.Println("Map was called")
	filename := HHH.File

	// intermediate := []KeyValue{}
	file, err := os.Open(filename)
	if err != nil {
		log.Fatalf("cannot open %v", filename)
	}
	content, err := ioutil.ReadAll(file)
	if err != nil {
		log.Fatalf("cannot read %v", filename)
	}
	file.Close()
	kva := mapf(filename, string(content))
	// intermediate = append(intermediate, kva...)

	sort.Sort(ByKey(kva))

	// fmt.Println(kva)

	// 中间文件
	FilePtrs := make([](*os.File), HHH.NReduce)
	FileNames := make([]string, HHH.NReduce)
	TempNames := make([]string, HHH.NReduce)

	var i int = 0
	for i = 0; i < len(FilePtrs); i++ {
		FileNames[i] = "mr-" + strconv.Itoa(HHH.TheNum) + "-" + strconv.Itoa(i)
		FilePtrs[i], _ = ioutil.TempFile("./", FileNames[i])
		TempNames[i] = FilePtrs[i].Name()
		// fmt.Println(FileNames[i], strconv.Itoa(i), TempNames[i])
	}

	for _, kv := range kva {
		Y := (ihash(kv.Key) % HHH.NReduce)
		enc := json.NewEncoder(FilePtrs[Y])
		enc.Encode(kv)
	}

	for _, x := range FilePtrs {
		x.Close()
	}
	//提交任务
	CommitMap(HHH, TempNames, FileNames)
}

func DoReduce(HHH Forjobreply, reducef func(string, []string) string) {
	// fmt.Println("Reduce was called")
	num := HHH.TheNum
	// fmt.Println(num)
	files := HHH.Intermediatefiles
	kva := []KeyValue{}
	for _, name := range files {
		if name[len(name)-1:] == strconv.Itoa(num) {
			// fmt.Println(name)
			file, _ := os.Open(name)
			dec := json.NewDecoder(file)
			for {
				var kv KeyValue
				if err := dec.Decode(&kv); err != nil {
					break
				}
				kva = append(kva, kv)
			}
		}
	}
	// fmt.Println(kva)

	sort.Sort(ByKey(kva))

	oname := "mr-out-" + strconv.Itoa(num)
	ofile, _ := os.Create(oname)

	i := 0
	for i < len(kva) {
		j := i + 1
		for j < len(kva) && kva[j].Key == kva[i].Key {
			j++
		}
		values := []string{}
		for k := i; k < j; k++ {
			values = append(values, kva[k].Value)
		}
		output := reducef(kva[i].Key, values)

		// this is the correct format for each line of Reduce output.
		fmt.Fprintf(ofile, "%v %v\n", kva[i].Key, output)

		i = j
	}

	ofile.Close()
	CommitReduce(HHH)
}
func CommitReduce(HHH Forjobreply) {
	args := Forjobargs{}
	args.Num = HHH.TheNum
	args.Mytime = HHH.Worktime
	reply := Forjobreply{}
	call("Master.HandinReduce", &args, &reply)
}

func CommitMap(HHH Forjobreply, temp []string, need []string) {
	args := Forjobargs{temp, need, HHH.TheNum, HHH.Worktime}
	reply := Forjobreply{}

	call("Master.HandinMap", &args, &reply)

	return

}

//
// example function to show how to make an RPC call to the master.
//
// the RPC argument and reply types are defined in rpc.go.
//
func Calljob() (Forjobreply, bool) {

	args := Forjobargs{}

	reply := Forjobreply{}

	state := call("Master.Askforjob", &args, &reply)

	return reply, state
}

//
// send an RPC request to the master, wait for the response.
// usually returns true.
// returns false if something goes wrong.
//
func call(rpcname string, args interface{}, reply interface{}) bool {
	// c, err := rpc.DialHTTP("tcp", "127.0.0.1"+":1234")
	sockname := masterSock()
	c, err := rpc.DialHTTP("unix", sockname)
	if err != nil {
		log.Fatal("dialing:", err)
	}
	defer c.Close()

	err = c.Call(rpcname, args, reply)
	if err == nil {
		return true
	}

	fmt.Println(err)
	return false
}
