import './globals.css'
import Header from '../components/Header'

export const metadata = {
  title: 'FinLit Sim',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Header />
        <main className="min-h-screen bg-slate-50 text-slate-900">{children}</main>
      </body>
    </html>
  )
}
