package mr

//
// RPC definitions.
//
// remember to capitalize all names.
//

import (
	"os"
	"strconv"
	"time"
)

const (
	EXIT   = -1
	MAP    = 1
	REDUCE = 2
	AWAIT  = 3 //待机

	UNALLOCATE = 0 //未分配
	WAIT       = 1 //已分配，等待中
	COMPLETED  = 2 //完成
)

//提交任务时
type Forjobargs struct {
	Tempfiles []string
	Filenames []string
	Num       int
	Mytime    time.Time
}

//返回任务时
type Forjobreply struct {
	JobType           int
	File              string
	Intermediatefiles []string
	TheNum            int //编号
	NReduce           int //reduce数量
	Worktime          time.Time
}

// Cook up a unique-ish UNIX-domain socket name
// in /var/tmp, for the master.
// Can't use the current directory since
// Athena AFS doesn't support UNIX-domain sockets.
func masterSock() string {
	s := "/var/tmp/824-mr-"
	s += strconv.Itoa(os.Getuid())
	return s
}
