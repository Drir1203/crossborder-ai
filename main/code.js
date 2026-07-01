class MyPromise {
  constructor(executor) {
    this.state = 'pending';
    this.value = undefined;
    this.reason = undefined;
    this.onFulfilled = []; // 成功回调池
    this.onRejected = [];  // 失败回调池

    const resolve = (value) => {
      if (this.state === 'pending') {
        this.state = 'fulfilled';
        this.value = value;
        this.onFulfilled.forEach(fn => fn());
      }
    };

    const reject = (reason) => {
      if (this.state === 'pending') {
        this.state = 'rejected';
        this.reason = reason;
        this.onRejected.forEach(fn => fn());
      }
    };

    try {
      executor(resolve, reject);
    } catch (err) {
      reject(err);
    }
  }

  then(onFulfilled, onRejected) {
    // 穿透处理（很重要，面试常问）
    onFulfilled = typeof onFulfilled === 'function' ? onFulfilled : v => v;
    onRejected = typeof onRejected === 'function' ? onRejected : err => { throw err };

    const promise2 = new MyPromise((resolve, reject) => {
      // 封装执行函数，为了复用
      const handle = (callback, valueOrReason) => {
        // 模拟微任务（面试说用 setTimeout 模拟异步就行）
        setTimeout(() => {
          try {
            const x = callback(valueOrReason);
            resolve(x); // 简版：直接 resolve，不深究 x 是 Promise 的情况
          } catch (err) {
            reject(err);
          }
        });
      };

      if (this.state === 'fulfilled') {
        handle(onFulfilled, this.value);
      } else if (this.state === 'rejected') {
        handle(onRejected, this.reason);
      } else {
        // pending 状态，存入回调池
        this.onFulfilled.push(() => handle(onFulfilled, this.value));
        this.onRejected.push(() => handle(onRejected, this.reason));
      }
    });

    return promise2;
  }
}