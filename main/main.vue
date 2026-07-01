

<script lang="ts">
const promiseAll = (promises:<T>) => {
    if(!Array.isArray(promises)){
        return TypeError('promise is not Array')
    }
    return new Promise((resolve, reject)=>{
        let count = 0;
        let results:any = []
        promises.forEach((promise,index)=>{
            Promise.resolve(promise).then(res=>{
                count++
                results[index] = res
            }).catch(reject)
        })
        if(count === promises.length) resolve(results)
    })
}

const deepConle = (target:any, map = new WeakMap()) => {
    if(target === null || typeof target !== 'object') return target
    if(map.has(target)) return map.get(target)
    if(target instanceof Date) return new Date(target)
    if(target instanceof RegExp) return new RegExp(target.source, target.flags)
    if(target instanceof Set){
        const set = new Set()
        map.set(target, set)
        target.forEach(val=>{
            set.add(deepConle(map,val))
        })
        return set
    }
    if(target instanceof Map){
        const cloneMap = new Map()
        map.set(target, cloneMap)
        target.forEach((val, key)=>{
            cloneMap.set(key, deepConle(val, map))
        })
        return cloneMap
    }
    const targetClone = Array.isArray(target) ? [] : {}
    const symbolKeys = Object.getOwnPropertySymbols(target)
    for(let symbolKey of symbolKeys){
         const value = target[symbolKey];
        if(typeof value === 'object' && value !== null){
            targetClone[symbolKey] = deepConle(map, value)
        }else{
            targetClone[symbolKey] = value
        }
    }
    for(let key in target ){
        if(target.hasOwnProperty(key)){
            const value = target[key]
            if(typeof value === 'object' && value !== null){
                targetClone[key] = deepConle(value, map)
            }else{
                targetClone[key] = value
            }
        }
    }
    return targetClone
}

const dobunce = (func, wait, immediate) => {
    let result = null
    let timeout = null
    const debounced = (...args) => {
        const context = this 
        if(timeout) clearTimeout(timeout)
        if(immediate){
            const callNow = !timeout
            setTimeout(()=>{
                timeout = null
            }, wait)
            result = func.apply(context, args)
        }else{
            setTimeout(()=>{
                result = func.apply(context,args)
            }, wait)
        }
    }
    debounced.closed = ()=>{
        timeout = null
        result = null
    }
    return debounced
}
const thrrote  = (func, wait) =>{
    let timeout = null
    return function(...args){
        let lastTime = 0
        let context = this
        const nowTime = Date.now()
        if(nowTime-lastTime >= wait){
            lastTime = nowTime
            return func.apply(context, args)
        }
    }
}
 Function.prototype.myApply = (context, args) => {
    const fn = Symbol('fn')
    context[fn] = this
    const result = context[fn](...args)
    delete context[fn]
    return result
 }

 const curry = (fn) => {
    const ans = fn.length
    return function(...args){
        if(ans >= args.length){
            return fn.apply(this, args)
        }else{
            
        }
    }
 }

 const debounce = (wait, func, immediate ) => {
    let result = null
    let timeout = null
    const debounced = (...args) => {
        const context = this
        if(timeout) clearTimeout(timeout)
        if(immediate){
            const callNow = !timeout
            setTimeout(()=>{
                timeout = null
            }, wait)
            if(callNow) result = func.apply(context, args)
        }else{
            timeout = setTimeout(()=>{
                timeout = null
                result = func.apply(context, args)
            }, wait)
        }
        return result
    }
    debounced.closed = () =>{
        timeout = null
        result =null
    }
    return debounced
 }

 //防抖
const debounce = (func, wait, immedidate) => {
    let timer = null
    let result = null
  const debounced = (...args) => {
    const context = this
    if(timer) clearTimeout(timer)
    if(immedidate){
        setTimeout(()=> {
            timer = null
        }, wait)
        const callNow = !timer
        if(callNow){
        result = func.apply(context, args)
        }
    }else{
        timer = setTimeout(()=>{
            timer = null
            result = func.apply(func, wait)
        }, wait)
    }
    return result
  }
  return debounced
}

const thrrot = (func, wait) => {
    return function(...args){
        let lastTime = 0
        const nowTime = Date.now()
        if(nowTime-lastTime>=wait){
            func.apply(this, args)
            lastTime  = nowTime
        }
    }
}

const thrrolt = () => {
    let timer = null
    return function(...args){
        if(!timer){
            timer = setTimeout(()=>{
                func.apply(this, args)
            }, timer)
        }
    }
}

Function.prototype.apply = (context = window, args) => {
    if(typeof this !== 'function'
    ){
        return new TypeError('this is not a function')
    }
    const fn = Symbol('fn')
    context[fn] = this
    let result = context[fn](...args)
    delete context[fn]
    return result
}

const promiseAll = (promises) => {
    return new Promise((resolve, reject)=>{
        let result = []
        let count = 0
        promises.forEach((promise, index)=>{
            Promise.resolve(promise).then(res=>{
                count++
                res[index] = res
                if(count === promises.length) resolve(res)
            }).catch(reject)
        })
    })
}
//柯里化
const curry = (fn) => {
  return function(){
    
  }
}




</script>