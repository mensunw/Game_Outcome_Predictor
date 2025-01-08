import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from '@/components/ui/card'

export default function Hero() {
    return (
        <section className="w-full p-6 pt-28 pb-12 mb-[20%]">
            <div className="container px-4 md:px-6">
                <div className="flex flex-col items-center space-y-6 text-center">
                    <div className="space-y-4">
                        <h2 className="text-5xl font-black tracking-tight max-w-[600px]">
                            Predict Game Outcomes With Unmatched Precision
                        </h2>
                    </div>
                </div>

                <Card className="bg-sky-100 ml-[18%] mr-[18%] mt-[5%]">
                    img here later
                </Card>
            </div>
        </section>
    )
}