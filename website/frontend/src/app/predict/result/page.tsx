'use client'

import { useSearchParams, notFound } from 'next/navigation';
import { Card, CardTitle } from '@/components/ui/card'
import Headline from "@/components/pages/predict/result/Headline";

const ResultPage: React.FC = () => {

    const searchParams = useSearchParams();
    const data = searchParams.get('data');
    if (!data) {
        notFound(); // Triggers the built-in 404 page
    }
    const result = data === 'true';

    return (
        <>
            <Headline />
            {result ? (
                <Card className="ml-[30%] mr-[30%] mt-[1%] mb-8 bg-green-300">
                    <CardTitle className="flex justify-center p-6 text-5xl font-black">
                        WIN (53%)
                    </CardTitle>
                </Card>
            ) :
                <Card className="ml-[30%] mr-[30%] mt-[1%] mb-8 bg-red-300">
                    <CardTitle className="flex justify-center p-6 text-5xl font-black">
                        LOSE (51%)
                    </CardTitle>
                </Card>
            }

        </>
    )
}

export default ResultPage