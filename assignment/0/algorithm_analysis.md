# 冒泡排序
这个最简单，外层N-1趟，内层N-1-i趟。$O(N^2)$
# 插入排序
考虑反序输入$\sum_{i=2}^Ni=2+...N=\varTheta(N^2)$
# 归并排序
对N个数归并排序用时=2*对N/2个数的归并排序+线性的合并时间
$T(N)=2T(N/2)+N$
$\frac{T(N)}{N}=\frac{T(N/2)}{N/2}+1$
$\frac{T(N/2)}{N/2}=\frac{T(N/4)}{N/4}+1$
...  
累加,左右相消,$T(N)=NlogN+N=O(NlogN)$
# 快速排序
平均情况分析，$T(N)=T(i)+T(N-i-1)+cN$(分割时间cN，分割后两部分大小不定)，假设均匀分布则，$T(N)=\frac{2}{N}\sum_{j=0}^{N-1}T(j)+cN$，进一步有$NT(N)-(N-1)T(N-1)=2T(N-1)+2cN-c$，化简、移项、同除N(N-1)得$\frac{T(N)}{N+1}=\frac{N-1}{N}+\frac{2c}{N+1}$,类似上面的方法，易得$T(N)=O(NlogN)$

# 堆排序
二叉堆(最小堆)的插入(上滤)以及删除最小元(下滤)均为$O(logN)$
则堆排序$O(2N*logN)+O(N)=O(NlogN)$