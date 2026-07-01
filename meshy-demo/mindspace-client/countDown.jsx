import useCountdown from '@/hooks/useCountdown'
;

export default function Countdown(
) {
  const seconds = useCountdown(10
);

  return
 (
    <div className="countdown">
      基础倒计时：{seconds} 秒
    </div>
  );
}