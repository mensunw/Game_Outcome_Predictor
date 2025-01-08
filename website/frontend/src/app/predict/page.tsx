'use client'

import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'
import Headline from "@/components/pages/predict/Headline";
import PredictForm from "@/components/pages/predict/PredictForm";

const PredictPage: React.FC = () => {
    return (
        <>
            <Headline />
            <PredictForm />

        </>
    )
}

export default PredictPage