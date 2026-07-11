const TECH_STACK = ['Vite', 'React', 'TypeScript', 'Tailwind CSS']
export default function HomePage(){
    return (
    <div className="flex min-h-screen flex-col items-center justify-center gap-6 px-6 text-center text-slate-100">
      <div className="rounded-2xl bg-slate-100 p-4 shadow-lg">
        <img src="/logo.png" alt="Logo" className="h-12 w-auto object-contain" />
      </div>

      <div className="space-y-3">
        <h1 className="text-3xl font-semibold tracking-tight sm:text-4xl">Šablona projektu</h1>
        <p className="max-w-md text-slate-400">
          Toto je výchozí šablona pro tvorbu dalších aplikací. Neobsahuje žádnou funkční logiku
          — jen předpřipravené prostředí, na kterém lze začít stavět.
        </p>
      </div>

      <div className="flex flex-wrap justify-center gap-2">
        {TECH_STACK.map((tech) => (
          <span
            key={tech}
            className="rounded-full border border-slate-800 bg-slate-900 px-3 py-1 text-sm text-slate-300"
          >
            {tech}
          </span>
        ))}
      </div>
    </div>
  )
}