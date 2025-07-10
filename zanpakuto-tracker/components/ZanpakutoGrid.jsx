export default function ZanpakutoGrid({ blades, onSelect }) {
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-6 p-2">
      {blades.map((z, i) => (
        <div
          key={i}
          onClick={() => onSelect(z)}
          className="bg-gray-900 border border-indigo-700 p-4 rounded-xl shadow hover:scale-105 cursor-pointer transition"
        >
          <h2 className="text-xl font-bold text-indigo-300">{z.name}</h2>
          <p className="text-sm text-gray-400">{z.kanji}</p>
          <p className="text-xs text-yellow-200 mt-1">{z.domain}</p>

          <ProgressBar label="Shikai" value={z.shikai_progress} color="green" />
          <ProgressBar label="Bankai" value={z.bankai_progress} color="red" />
        </div>
      ))}
    </div>
  );
}

function ProgressBar({ label, value, color }) {
  const colorMap = {
    green: "bg-green-500",
    red: "bg-red-500",
    blue: "bg-blue-500",
  };

  return (
    <div className="mt-2">
      <div className="flex justify-between text-xs text-gray-300">
        <span>{label}</span>
        <span>{value}%</span>
      </div>
      <div className="w-full bg-gray-700 rounded h-2 mt-1">
        <div
          className={`${colorMap[color]} h-2 rounded`}
          style={{ width: `${value}%` }}
        />
      </div>
    </div>
  );
}
