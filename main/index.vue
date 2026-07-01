<template> 
    <div class="main-index">
        TEST
        <div>

        </div>
    </div> 

</template>
<script setup>
//leetcode实现
//防抖 - n秒内频繁调用函数，只会执行最后一次调用，也就是n秒内多次调用，则清空计时器重新计时n秒，n秒后执行最后一次调用
const debounce = (func, await) => {
 let timer = null
return function(...args){
    const context = this
    if(timer) clearTimeout(timer) //清楚定时器重新计算时间
    timer = setTimeout(()=>{

        timer = null
        func.apply(context, args)
    }, await)
}
}/*  */
//节流
const thrrtol = (func, wait) => {
    let timer = null
    return function(...args){
        const context = this
        if(!timer){
            timer = setTimeout(()=> {
                func.apply(context,args)
                timer = null
            }, wait)
        }
    }
}
//深拷贝
const deepClone = (target, map = new WeakMap()) =>{
 if(target ==null || target == undefined) return target
 if(typeof target !== 'object') return target
//判断是否为普通循环对象
if(map.has(target)){
    return map.get(target)
}
//date
if(target instanceof Date){
    return new Date(target)
}

//regexp
if(target instanceof RegExp){
  return new RegExp(target.source, target.flags)
}

let cloneTarget = Array.isArray(target) ? [] : {}
//判断是否为symbols嵌套 //获取symbol属性
const symbolKeys = Object.getOwnPropertySymbols(target)
for(const symKey in symbolKeys){
    //
    if(typeof symKey == 'object' && key !== null){
        cloneTarget[symKey] = deepClone(target[symKey], map)    
    }else{
        cloneTarget[symKey] = target[symKey]
    }
}

//如果是对象
for(let key in target){
    if(Object.defineProperty.toString.call(target, key)){
        if(typeof key == 'object' && key !== null){
            cloneTarget[key] = deepClone(key, map)
        }else{
            cloneTarget[key] = target[key]
        }
    }
}
return cloneTarget
}

const promiseAll = (promises) => {
 return new Promise((resolve, reject)=> {
    let count = 0;
    let result = []
    promises.forEach((promise)=> {
       Promise.resolve(promise).then((res)=>{
        result.push(res)
        count++
       })
    })
 })
}


//手写Promise all方法
const promiseAll = (promises) => {
    return new Promise((resolve, reject) => {
        let result = []
        let count = 0
        promises.forEach(promise => {
            Promise.resolve(promise).then(res =>{
                result.push(res)
                if(++count == promises.length) resolve(result) //执行完成全部promise
            }).catch(reject)
        });
        if(!promises?.length) resolve(result)
    })
}

Function.prototype.myBind = (context = window, ...args) =>{
  const fn = Symbol('fn')
  context[fn] = this
  const result = context[fn](...args)
  delete context[fn]
  return result
}

const promiseAll = (promises) => {
  let result = []
  let count = 0
  return new Promise((resolve, reject) => {
    promises.forEach((promise) => {
      Promise.resolve(promise).then(res=> {
        count++
        result.push(res)
      }).catch(reject)
    })
  })
  if(count === promises.length) return result
}

//LCR 016
// . 无重复字符的最长子串
var lengthOfLongestSubstring = function(s) {
  let result = []
  let max = 0
  for(let i = 0; i<s.length; i++){
     let index = result.indexOf(s[i]) //判断当前字符是否已经存在
     if(index > -1){
        result.splice(0, index+1)
     }
     result.push(s[i])
     max =  Math.max(result.length, max)
  }
  return max
};

//防抖
const deBounce = (func, wait) => {
    let timer = null
    return function(...args){
        if(timer) clearTimeout(timer)
        let context = this
        timer = setTimeout(()=>{
            timer = null
            func.apply(context, args)
        }, wait)
    }
}

const thrrotle = (func, wait) => {
    let timer =null
    return function(...args){
        let context = this
        timer = setTimeout(()=>{
            func.apply(context, args)
            timer = null
        }, await)
    }
}

Function.prototype.myCall = (context = window, ...args)=>{
 if(typeof this !== 'function'){
    throw TypeError('Error')
 }
 const fn = Symbol('fn')
 context[fn] = this
 const result = context[fn](...args)
 delete context[fn]
 return result
}

Function.prototype





Function.prototype.myCall = function(context = window, ...args) {
  if (typeof this !== 'function') {
    throw new TypeError('Error');
  }

  const fn = Symbol('fn');
  context[fn] = this;
  const result = context[fn](...args);
  delete context[fn];
  return result;
};

// apply实现
Function.prototype.myApply = function(context = window, args = []) {
  if (typeof this !== 'function') {
    throw new TypeError('Error');
  }

  const fn = Symbol('fn');
  context[fn] = this;
  const result = context[fn](...args);
  delete context[fn];
  return result;
};

// bind实现
Function.prototype.myBind = function(context = window, ...args) {
  if (typeof this !== 'function') {
    throw new TypeError('Error');
  }

  const self = this;

  const fBound = function(...innerArgs) {
    // 判断是否作为构造函数调用
    return self.apply(
      this instanceof fBound ? this : context,
      args.concat(innerArgs)
    );
  };

  // 维护原型关系
  fBound.prototype = Object.create(self.prototype);

  return fBound;
};


//322. 零钱兑换
/**
 * @param {number[]} coins
 * @param {number} amount
 * @return {number}
 *首先分析该题是用了什么算法，凡是求最值一般都是动态规划，然后动态规划一般都是拆分成多个独立的简单子问题来求解
   所以求amount所需的最少的硬币个数，可以看成是amount-coins的子集所用的最小硬币数+1，最后递归去拆分成简单的子集
 */
var coinChange = function(coins, amount) {
    //对0-amount之间的硬币值所需的最小硬币个数进行求解，组成数组dp[],其中dp[amount]也就是amount对应所需的字少硬币个数
    if(!amount) return 0
    let dp = new Array(amount+1).fill(Infinity)
    dp[0] = 0
    for(let i = 0; i < coins.length; i++){
        for(let j = coins[i]; j <= amount; j ++){
            dp[j] = Math.min(dp[j], dp[j-coins[i]]+1)
        }
    }
    return dp[amount] == Infinity ? -1 : dp[amount]
};

560. 和为 K 的子数组
/**
 * @param {number[]} nums
 * @param {number} k
 * @return {number}
 */
var subarraySum = function(nums, k) {
    const s = new Array(nums.length+1).fill(0)
    for(let i = 0;i <nums.length;i++){
        s[i+1] = s[i]+nums[i]
    }
    const map = new Map()
    let ans = 0
    for(let st of s){
        if(map.get(st-k))ans+=(map.get(st-k)??0)
        map.set(st, (map.get(st)?? 0 )+1)
    }
    return ans
};

function debounce(func, wait, immediate = false) {
  let timeout = null;
  let result;

  const debounced = function(...args) {
    const context = this;

    // 如果已有定时器，清除它
    if (timeout) clearTimeout(timeout);

    // 立即执行模式
    if (immediate) {
      // 如果没有定时器，表示可以立即执行
      const callNow = !timeout;
      timeout = setTimeout(() => {
        timeout = null;
      }, wait);
      if (callNow) result = func.apply(context, args);
    } else {
      // 非立即执行模式
      timeout = setTimeout(() => {
        result = func.apply(context, args);
      }, wait);
    }

    return result;
  };

  // 取消方法
  debounced.cancel = function() {
    clearTimeout(timeout);
    timeout = null;
  };

  return debounced;
}

//防抖
const debounce = (func, wait, immediate) => {
  let timeout = null
  let result; 
  const debounced = (...args) => {
    let context = this
      if(timeout) clearTimeout(timeout)
      //立即执行
      if(immediate){
        const callNow = !timeout
        setTimeout(()=>{
            timeout = null
        }, wait)
        if(callNow) result = func.apply(context, args)
      }else{
        timeout = setTimeout(()=>{
            func.apply(context, args)
        }, wait)
      }
  }
  //取消方法
  debounced.canceld = () => {
    clearTimeout(timeout)
    timeout = null
  }
}

// 节流函数
const throttle = (func, wait) => {
    let lastTime = 0
    return function(...args){
        let context = this
        const nowTime= Date.now()
        if(nowTime-lastTime >=wait){
            lastTime = nowTime
            func.apply(context, args)
        }
    }
}

const thrrotl = (func, wait) => {
  let lastTime = 0
  return function(...arg){
    let context = this 
    const nowTime = Date.now()
    if(nowTime-lastTime >= wait){
      lastTime = nowTime
      func.apply(context, args)
    }
  }
}

function throttle(func, wait, options = {}) {
  let timeout = null;
  let previous = 0; //上次执行的时间戳
  const { leading = true, trailing = true } = options;

  const throttled = (...args) =>{
    const context = this;
    const now = Date.now();

    // 如果不是立即执行，并且previous为0（第一次执行）
    if (!previous && !leading) previous = now;

    const remaining = wait - (now - previous);

    if (remaining <= 0 || remaining > wait) {
      if (timeout) {
        clearTimeout(timeout);
        timeout = null;
      }
      previous = now;
      func.apply(context, args);
    } else if (!timeout && trailing) {
      timeout = setTimeout(() => {
        previous = !leading ? 0 : Date.now();
        timeout = null;
        func.apply(context, args);
      }, remaining);
    }
  };
  throttled.canceld = () => {
    clearTimeout(timeout)
    previous = 0
    timeout = null
  }
  return throttled

}
Function.prototype.apply = (context, args) => {
  const fn = Symbol('fn')
  context[fn] = this
  let result = context[fn](...args)
  delete context[fn]
  return result
}

const debounce = (func, wait, immediate) => {
  let timeout =null
  const debounced = (...args) =>{
    let context = this
    let result = null
    if(timeout) clearTimeout(timeout)
    if(immediate){
      setTimeout(()=>{
        timeout = null
      }, wait)
      const callNow = !timeout
      if(callNow) result = func.apply(context, args)
    }else{
      setTimeout(()=>{
        timeout = null
        result = func.apply(context, args)
      }, wait)
    }
  }
  return debounced
}
</script>

async function async1() {
  console.log('async1 start')
  await async2()
  console.log('async1 end')
}
async function async2() { console.log('async2') }
console.log('script start')
setTimeout(() => { console.log('setTimeout') }, 0)
async1()
new Promise(resolve => {
  console.log('promise1')
  resolve()
}).then(() => { console.log('promise2') })
console.log('script end')
script start
async1 start
async2

