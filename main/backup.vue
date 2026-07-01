<script setup>

const deepClone = (target, map = new Map()) => {
    //普通数据类型
 if(target == null || typeof target != 'object') return target
 if(map.has(target)) return map.get(target) //循环引用
 if(target instanceof Date) return new Date(target.getTime()) //日期
 if(target instanceof RegExp) return new RegExp(target.source, target.flags) //正则
 if(target instanceof Set){ //set
    const cloneSet = new Set()
    map.set(target, cloneSet)
    target.forEach(val => {
        cloneSet.add(deepClone(val, map))
    })
    return cloneSet
 }
 if(target instanceof Map){
    const cloneMap = new Map()
    map.set(target, cloneMap)
    target.forEach((val, key) =>{
        cloneMap.set(key, deepClone(val, map))
    })
    return cloneMap
 }
 //symbols
 const targetClone = Array.isArray(target) ? [] : {}
 const symbols = Object.getOwnPropertySymbols(target)
 for(let symbolKey of symbols){
    if(symbolKey !== null && typeof symbolKey === 'object'){
        targetClone[symbolKey] = deepClone(target[symbolKey],map )
    }else{
        targetClone[symbolKey] = target[symbolKey]
    }
 }
 //普通对象属性
 for(let key in target){
    if(target.hasOwnProperty(key)){
        if(target[key]!== null && typeof target[key] == 'object'){
            targetClone[key] = deepClone(target[key],map)
        }else{
            targetClone[key] = target[key]
        }
    }
 }
 return targetClone
}

const promiseAll = (promises) => {
    if(!Array.isArray(promises)) return TypeError('promises is not a array')
    return new Promise((resolve, reject) => {
        let count = 0
        let results = []
        promises.forEach((promise, index)=>{
            Promise.resolve(promise).then(res=>{
                count++
                results[index] = res
                if(count === promises.length) resolve(results)
            }).catch(reject)
        })
    })
}

const curry = (fn) => {
    const ans = fn.length 
    return function(...args){
        if(args.length === ans){
            return fn.apply(this, args)
        }else{
            return (...moreArgs)=> curry(fn).apply(this, [...args, ...moreArgs])
        }
    }
}

const flatten = (arr) => {
    let result = []
    for(let item of arr){
        if(Array.isArray(item)){
            result = result.contact(flatten(item))
        }else{
            result.push(item)
        }
    }
    return result
}

Function.prototype.myApply= (context, args)=>{
    const fn = Symbol('fn')
    context[fn] = this
    const result = context[fn](...args)
    delete context[fn]
    return result
}




</script>