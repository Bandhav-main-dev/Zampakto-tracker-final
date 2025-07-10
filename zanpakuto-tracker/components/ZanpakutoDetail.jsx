import { useState } from "react";

export default function ZanpakutoDetail({ blade, goBack }) {
  const [tasks, setTasks] = useState(blade.shikai_tasks || []);

  return (
    <div className="p-4">
      <button onClick={goBack} className="text-indigo-400 hover:underline mb-4">← Back to Blades</button>
      
      <h2 className="text-3xl font-bold text-indigo-300 mb-2">{blade.name}</h2>
      <p className="text-sm text-gray-400 italic">{blade.kanji} – {blade.domain}</p>
      <p className="text-sm text-yellow-300 mt-1">Release: <span className="italic">"{blade.release_command}"</span></p>

      <section className="mt-6">
        <h3 className="text-xl font-semibold text-green-300 mb-2">🟢 Shikai Tasks</h3>
        {blade.shikai_tasks.map((task, index) => (
          <TaskCard key={index} task={task} />
        ))}
      </section>

      <section className="mt-6">
        <h3 className="text-xl font-semibold text-red-300 mb-2">🔴 Bankai Tasks</h3>
        {blade.bankai_tasks.map((task, index) => (
          <TaskCard key={index} task={task} />
        ))}
      </section>
    </div>
  );
}

function TaskCard({ task }) {
  return (
    <div className="bg-gray-800 p-3 rounded-lg mb-3 border border-gray-600">
      <p className="text-sm text-white">🔹 {typeof task === "string" ? task : task.task}</p>
    </div>
  );
}
