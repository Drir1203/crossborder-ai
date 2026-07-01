import { useState, useEffect, useRef } from 'react';

export function useCountDown(initSeconds: number) {
    const [seconds, setSecond] = useState(initSeconds)
    const timeRef = useRef<ReturnType<typeof setTimeout> | null>(null)
    const mountedRef = useRef(true)
    useEffect(() => {
        if (seconds <= 0) return
        timeRef.current = setTimeout(() => {
            if (mountedRef.current) {
                setSecond(v => v - 1)
            }
        }, 1000)
        return () => {
            if (timeRef.current) {
                clearTimeout(timeRef.current)
            }
        }
    }, [seconds])
    useEffect(() => {
        return () => {
            mountedRef.current = false
        }
    }, [])
    return seconds
}