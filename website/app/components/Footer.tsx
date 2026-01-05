export function Footer() {
  return (
    <footer className="py-12 px-6 border-t border-[#E5E7EB]">
      <div className="max-w-[700px] mx-auto text-center">
        <div className="flex items-center justify-center gap-6 text-sm text-[#6B7280] flex-wrap mb-4">
          <a href="https://github.com/tomalmog/tempo" className="hover:text-[#1A1A1A] transition-colors">
            GitHub
          </a>
          <a href="https://github.com/tomalmog/tempo#readme" className="hover:text-[#1A1A1A] transition-colors">
            Documentation
          </a>
          <a href="https://github.com/tomalmog/tempo/issues" className="hover:text-[#1A1A1A] transition-colors">
            Support
          </a>
        </div>
        <div className="text-sm text-[#9CA3AF]">
          MIT License · Made for developers who sleep
        </div>
      </div>
    </footer>
  )
}

