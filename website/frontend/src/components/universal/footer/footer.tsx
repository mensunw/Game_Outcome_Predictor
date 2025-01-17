/* 
From CodeHive project
*/
import Link from 'next/link'
import siteConfig from '@/components/universal/footer/site-config'
import { Linkedin, Instagram, Facebook, Twitter } from 'lucide-react'

export default function SiteFooter() {
    return (
        <footer className="border-t border-border/40 bg-primary md:px-8 md:py-0">
            <div className="container flex justify-center pt-8">
                <p className="text-balance text-center font-body text-white text-base leading-loose md:text-lg">
                    Built by Mensun Wang. Check me out on{' '}
                    <Link
                        href={siteConfig.links.github}
                        className="font-medium underline underline-offset-4 hover:text-black"
                        target="_blank"
                        rel="noreferrer"
                        aria-label="Visit GitHub (opens in a new tab)"
                    >
                        GitHub
                    </Link>
                    .
                </p>
            </div>
            <div className="container flex flex-col items-center justify-center gap-4 py-6 md:flex-row">
                <p className="text-balance text-center text-sm leading-loose text-white">
                    &copy; 2025 Game Outcome Predictor
                </p>
                <Link
                    href="/terms-of-service"
                    className="text-balance text-center text-sm text-white leading-loose underline underline-offset-4 hover:text-muted-foreground"
                >
                    Terms
                </Link>
                <Link
                    href="/privacy-policy"
                    className="text-balance text-center text-sm text-white leading-loose underline underline-offset-4 hover:text-muted-foreground"
                >
                    Privacy
                </Link>
                <Link
                    href="/code-of-conduct"
                    className="text-balance text-center text-sm text-white leading-loose underline underline-offset-4 hover:text-muted-foreground"
                >
                    Code of Conduct
                </Link>
                <Link
                    href="mailto:mensun@bu.edu"
                    className="text-balance text-center text-sm text-white leading-loose underline underline-offset-4 hover:text-muted-foreground"
                >
                    Contact
                </Link>
                {/* Social Links */}
                <div className="flex space-x-4">
                    {' '}
                    {[Linkedin, Instagram, Facebook, Twitter].map((Icon, index) => (
                        <a
                            key={index}
                            href="https://www.linkedin.com/in/mensun/"
                            className="transition-colors duration-300 text-white hover:text-muted-foreground"
                        >
                            <Icon size={24} />{' '}
                            <span className="sr-only">Social Media Link</span>{' '}
                        </a>
                    ))}
                </div>
            </div>
        </footer>
    )
}