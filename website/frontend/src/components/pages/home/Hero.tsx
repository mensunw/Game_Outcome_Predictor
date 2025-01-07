import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export default function Hero() {
    return (
        <section className="w-full mt-12 p-6 pb-12 bg-amber-50 mb-36">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center space-y-6 text-center">
                    <div className="space-y-4">
                        <h2 className="text-3xl font-bold tracking-tight">
                            FF Detector
                        </h2>
                        <p className="text-p1 mx-auto max-w-[700px] text-muted-foreground md:text-xl font-body">
                            Ready to take your gameplay strategy to the next level? Look no further than the FF Detector! With its advanced prediction capabilities, you can make informed decisions in your games and maximize your win potential right from the 15-minute mark.
                        </p>

                    </div>

                </div>
            </div>
        </section>
    )
}