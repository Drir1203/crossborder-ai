
//数组扁平化-迭代和栈
const flatten = (arr) => {
    //初始化栈
    const stack = [...arr]
    let result = []
    while(stack.length){
        const item = stack.pop()
        if(Array.isArray(item)){
            for(let i = item.length-1; i>=0;i--){
                stack.push(item[i])
            }
        }else{
            result.push(item)
        }
    }
    return result.reverse()
}


//防抖
const debounce = (func, wait, options) => {
    let timer = null
    const { leading = false, trailing = true } = options || {}
    let previous = 0 //记录上次执行的时间
    return function(...args){
        const now = Date.now()
        const callNow = leading && (now-previous > wait || previous === 0)
        if(timer) clearTimeout(timer)
        //立即执行
        if(callNow){
            previous = now
            func.apply(this, args)
        }

        //延迟执行
        if(trailing){
            timer = setTimeout(()=>{
                if(!leading || (now-previous>=wait)){
                    func.apply(this, args)
                    previous = Date.now
                }
                timer = null

            }, wait)
        }
    }
}

const debounce = (wait, func, options) =>{
    const { leading = false , trailing = true } = options
    let timer = null
    let previous = 0
    return function(...args){
        const now = Date.now()
        if(timer) clearTimeout(timer)
        const callNow = leading &&(previous === 0 || (now-previous> wait))
        if(callNow){
            previous = now
            func.apply(this, args)
        }

        if(trailing){
            timer = setTimeout(()=>{
                if(!leading || (now-previous>=wait)){
                    func.apply(this, args)
                    previous = Date.now()
                }
                timer = null          },wait)
        }
    }
}

const thrrotle = (func, wait, options) => {
    const { leading = true, trailing = false } = options
    let timer = null
    let previous = 0
    return function(...args){
        let now = Date.now()
        if(!leading && previous === 0){
            previous = now
        }
        const remaining = wait - (now-previous)
        if(remaining<=0){
            if(timer){
                clearTimeout(timer)
                timer = null
            }
            func.apply(this, args)
        }else if(trailing && !timer){
            timer = setTimeout(()=>{
                previous = leading ? Date.now() : 0
                func.apply(this, args)
            }, remaining)
        }
    }
}

//数组扁平化转tree map缓存-遍历两次list 时间复杂度O(n)
const arrayToTree = (list,  rootId ) => {
    const map = new Map()
    let tree = []
    //首次遍历，将节点item存入map
    list.forEach(item => {
        map.set(item.id, {
            ...item,
            children: []
        })
    });
    list.forEach(item => {
        const node = map.get(item.id)
        const parent = map.get(item.parentId) //获取父节点
        if(parent){
            parent.chidren.push(node)
        }else if(item.parentId === rootId){
            tree.push(node)
        }
    });
    return tree
}

//tree转数组扁平化
const treeToArray = (tree, parentId) => {
    let result = []
    function dfs(nodes,pid ) => {
        nodes.forEach(node => {
            const { children, ...rest } = node
            result.push({
                ...rest,
                parentId: pid
            })
            if(children && children.length){
                dfs(children, node.id)
            }
        });
    }
    dfs(tree, parentId)
    return result
}



const debounce = (wait, func, options) => {
    let timer = null
    let previous = 0
    return function(...args){
        const { leading = false, trailing = true } = true
        const now = Date.now()
        const callNow = leading && (previous === 0 || (now-previous)>wait)
        if(timer) clearTimeout(timer)
        if(callNow){
            previous = now
            func.apply(this, args)
        }

        if(trailing){
            timer = (()=>{
                if(!leading || now-previous>=wait){
                    previous = Date.now()
                    func.apply(this, args)
                }
                timer = null
            },wait)

        }
    }   
}

const thrrotle = (func, wait, options ) => {
    let timer = null
    let preoius = 0 
    return function(...args){
        const { leading = true, trailing = false } = options
        const now  = Date.now()
        if(!leading && preoius === 0){
            preoius = now
        }
        const remaing = wait - (now-preoius)
        if(remaing<=0){
            if(timer){
                clearTimeout(timer)
                timer = null
            }
            func.apply(this, args)
        }else if(trailing && !timer){
            timer = setTimeout(()=>{
                preoius = leading ? Date.now() ? 0
                func.apply(this, args)
            }, remaing)
        }
    }
}

const promiseAll = (promises) => {
    return new Promise((resolve, reject)=>{
        if(!promises.length) return resolve([])
        let result = []
        let count = 0
        promises.forEach((promise, index) => {
            Promise.resolve(promise).then(res=>{
                count++
                result[index] = res
                if(count === promises.length) resolve(result)
            }).catch(reject)
        });
    })
}

//手写promise并发调度 - 边界条件 终止条件 处理条件
const promiseTool = (tasks, max) => {
    return new Promise((resolve, reject)=>{
        let result = []
        let index = 0
        let running = 0
        if(!tasks || tasks.length === 0) return resolve([])
        function runNext(){
            if(index === tasks.length && running === 0) return resolve(result)
                while(index < tasks.length && running < max){
                    let currentIndex = index++
                    let task = tasks[currentIndex]
                    Promise.resolve(task()).then(res=>{
                        result[currentIndex] = res
                    }).catch(error=> reject(error)).finally(()=>{
                        running--
                        runNext()
                    })
                }
        }
        runNext()
    })
}

const promiseTool = (tasks, max) => {
  return new Promise((resolve, reject)=>{
    let result = []
    let running = 0 
    let index = 0
    if(!tasks || tasks.length) return resolve([])
    function runNext(){
        if(index === tasks.length && running === 0){
            return resolve(result)
        }
        while(index < tasks.length &&running < max){
            const currentIndex = index++
            const task = tasks[currentIndex]
            Promise.resolve(task).then(res=>{
                result[currentIndex] = res
            }).catch(error=>reject(error)).finally(()=>{
                running--
                runNext()
            })
        }
    }
    runNext()
  })
}

//Event bus 解决跨组件通讯

Function.prototype.apply = (context = window, args: any) => {
    const fn = Symbol('fn')
    context[fn] = this
    let result = arsg ? context[fn](...args) : context[fn]()
    delete context[fn]
    return result
}


/**
 * 自定义 bind 方法
 * @param {Object} context 要绑定的 this 对象
 * @param {...any} args 预设参数（柯里化）
 */
Function.prototype.myBind = function(context, ...args) {
    const originalFn = this; // 保存原函数

    // 定义一个中转构造函数，用于原型链继承
    const fNOP = function() {};

    const boundFn = function(...innerArgs) {
        // 判断是否是 new 调用
        // 如果是 new，this 指向实例，应该绑定到实例上；否则绑定到 context
        const finalContext = this instanceof boundFn ? this : context;
        
        // 合并参数：bind 时的参数 + 调用时的参数
        return originalFn.apply(finalContext, [...args, ...innerArgs]);
    };

    // 维护原型链（关键步骤）
    // 让 boundFn 继承原函数 prototype 上的属性和方法
    fNOP.prototype = originalFn.prototype;
    boundFn.prototype = new fNOP();

    return boundFn;
};


const deepClone = (map = WeakMap(), target) => {

}