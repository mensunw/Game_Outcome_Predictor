"use client";
import InView from "@/components/ui/in-view";
import { Card, CardTitle } from '@/components/ui/card'

export default function Info() {
    return (
        <div className="relative mt-[15%] bg-sky-50 pb-64 overflow-x-hidden">
            <hr />
            <div className="py-6 text-center text-base font-medium">Scroll down</div>
            <div className="flex items-end justify-center px-4">
                <InView
                    variants={{
                        hidden: {
                            opacity: 0,
                            x: 160,
                        },
                        visible: {
                            opacity: 1,
                            x: 0,
                        },
                    }}
                    transition={{ duration: 0.3, ease: "easeInOut" }}
                    viewOptions={{ margin: "0px 0px -350px 0px" }}
                >
                    <Card className="bg-sky-100 ml-[18%] mr-[18%] mt-[5%] px-4 py-12">
                        <CardTitle className="flex text-2xl justify-center"> Model Details </CardTitle>
                        <p className="text-xl text-gray-600">
                            After exploring predictive modeling, I achieved a <strong className="text-gray-700">53%</strong> accuracy in forecasting game outcomes—a promising step toward understanding competitive dynamics. This was made possible using a <strong className="text-gray-700">Decision Trees</strong> classification model, a method that aligns precision with simplicity to deliver meaningful insights.
                        </p>
                    </Card>

                    <Card className="bg-sky-100 ml-[18%] mr-[18%] mt-[5%] px-4 py-12">
                        <CardTitle className="flex text-2xl justify-center"> Data Details </CardTitle>
                        <p className="text-xl text-gray-600">
                            To train the model, I utilized data from over <strong className="text-gray-700">10,000 </strong> matches, carefully selecting players from <strong className="text-gray-700">Silver</strong>, <strong className="text-gray-700">Gold</strong>, and <strong className="text-gray-700">Platinum</strong> tiers to strike a balance between accessibility and competitiveness. This effort was backed by an entire <strong className="text-gray-700">year</strong> of rigorous data collection, ensuring the predictions are both meaningful and impactful.
                        </p>
                    </Card>

                </InView>
            </div>
        </div>
    );
};
