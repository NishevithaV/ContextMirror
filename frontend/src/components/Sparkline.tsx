type Props = {
  values: number[];
  color?: string;
  width?: number;
  height?: number;
};

export function Sparkline({
  values,
  color = "#4F7CFF",
  width = 80,
  height = 28,
}: Props) {
  if (values.length === 0) return null;
  const max = Math.max(...values);
  const min = Math.min(...values);
  const range = max - min || 1;
  const stepX = width / (values.length - 1 || 1);

  const points = values.map((v, i) => {
    const x = i * stepX;
    const y = height - ((v - min) / range) * height;
    return `${x},${y}`;
  });

  const d = `M ${points.join(" L ")}`;
  const areaD = `${d} L ${width},${height} L 0,${height} Z`;

  return (
    <svg width={width} height={height} className="overflow-visible">
      <path d={areaD} fill={color} opacity={0.12} />
      <path d={d} fill="none" stroke={color} strokeWidth={1.5} />
    </svg>
  );
}

type BarsProps = {
  values: number[];
  color?: string;
  width?: number;
  height?: number;
};

export function Bars({
  values,
  color = "#A78BFA",
  width = 80,
  height = 28,
}: BarsProps) {
  if (values.length === 0) return null;
  const max = Math.max(...values) || 1;
  const gap = 2;
  const barWidth = (width - gap * (values.length - 1)) / values.length;

  return (
    <svg width={width} height={height}>
      {values.map((v, i) => {
        const h = (v / max) * height;
        return (
          <rect
            key={i}
            x={i * (barWidth + gap)}
            y={height - h}
            width={barWidth}
            height={h}
            rx={1.5}
            fill={color}
            opacity={0.8}
          />
        );
      })}
    </svg>
  );
}
