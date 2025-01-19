import Image from 'next/image'

export default function Hero() {
    return (
        <section className="flex flex-col p-6 pt-16 pb-12 items-center">
            <div className="container px-4">
                <div className="flex flex-col items-center space-y-6 mb-6 text-center">
                    <div className="space-y-4">
                        <h2 className="text-5xl font-black stracking-tight max-w-[600px]">
                            Predict Game Outcomes With <span className="bg-gradient-to-r from-sky-300 to-sky-500 bg-clip-text text-transparent">Unmatched Precision </span>
                        </h2>
                    </div>
                </div>
                <Image
                    src="/hero_img.png"
                    className="mx-auto block"
                    alt="hero img"
                    width={900}
                    height={900}
                />
            </div>
        </section>
    )
}