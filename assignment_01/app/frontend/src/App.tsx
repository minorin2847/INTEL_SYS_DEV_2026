import { useEffect, useState, type CSSProperties } from 'react';
import { HomePage } from './pages/HomePage';
import { ResultPage } from './pages/ResultPage';
import { usePathname, navigate } from './lib/router';
import { HeartPulse, Moon, Sun } from 'lucide-react';
import heroImage from './assets/hero-diabetes.jpg';

function App() {
  const pathname = usePathname();
  const [isDarkMode, setIsDarkMode] = useState(() => {
    const dark = localStorage.getItem('theme') !== 'light';
    // Applied synchronously (before first paint) to avoid a light-theme flash
    // when the user's stored preference is dark.
    document.documentElement.classList.toggle('dark', dark);
    return dark;
  });

  useEffect(() => {
    document.documentElement.classList.toggle('dark', isDarkMode);
    localStorage.setItem('theme', isDarkMode ? 'dark' : 'light');
  }, [isDarkMode]);

  const resultMatch = pathname.match(/^\/result\/([^/]+)\/?$/);

  return (
    <div className="app-shell min-h-screen relative overflow-hidden">
      <div className="mx-auto flex w-full max-w-7xl flex-col gap-6 px-4 py-5 sm:px-6 lg:px-8">
        <header className="top-bar relative z-10 flex items-center justify-between gap-4">
          <button
            type="button"
            onClick={() => navigate('/')}
            className="flex min-w-0 items-center gap-3 text-left"
          >
            <div className="brand-mark">
              <HeartPulse className="h-6 w-6 text-white" />
            </div>
            <div className="min-w-0">
              <p className="text-xs font-semibold uppercase tracking-wide text-[var(--app-primary)]">AI Clinical Lab</p>
              <h1 className="truncate text-xl font-bold text-[var(--app-text)] sm:text-2xl">
                Diabetes Predictor
              </h1>
            </div>
          </button>
          <button
            type="button"
            onClick={() => setIsDarkMode(prev => !prev)}
            className="theme-toggle shrink-0 rounded-lg p-3 transition-transform hover:-translate-y-0.5 active:translate-y-0"
            aria-label={isDarkMode ? 'Switch to light mode' : 'Switch to dark mode'}
            title={isDarkMode ? 'Light mode' : 'Dark mode'}
          >
            {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-primary-600" />}
          </button>
        </header>

        {!resultMatch && (
          <section
            className="hero-band has-photo relative z-10"
            style={{ '--hero-photo': `url(${heroImage})` } as CSSProperties}
          >
            <div className="hero-copy">
              <h2>From a finger-prick reading to a clear risk picture.</h2>
              <p>
                Diabetes Predictor takes a patient's routine clinical measurements — glucose,
                BMI, blood pressure, and more — and runs them through six trained machine
                learning models at once. Instead of one black-box answer, you get a ranked
                comparison of accuracy and F1 across all six models, plus a SHAP breakdown of
                exactly which factors pushed each verdict toward or away from a diabetes
                diagnosis.
              </p>
            </div>
          </section>
        )}

        {resultMatch ? <ResultPage resultId={resultMatch[1]} /> : <HomePage />}
      </div>
    </div>
  );
}

export default App;
