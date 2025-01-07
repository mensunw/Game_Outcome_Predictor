'use client'

import Image from "next/image";
import React, { useEffect, useState } from 'react';
import Testimonials from '@/components/pages/home/Testimonials'

export default function Home() {
  const [backendMessage, setBackendMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/test/")
      .then((response) => response.json())
      .then((data) => setBackendMessage(data.message))
      .catch((error) => console.error("Error fetching from backend:", error));
  }, []);

  return (
    <div className="grid grid-rows-[20px_1fr_20px] items-center justify-items-center min-h-screen p-8 pb-20 gap-16 sm:p-20 font-[family-name:var(--font-geist-sans)]">
      <div className="min-h-screen flex items-center justify-center bg-gray-100">
        <div className="p-6 bg-white rounded-lg shadow-lg text-center">
          <h1 className="text-2xl font-bold text-blue-500">React & Django Test</h1>
          <p className="mt-4 text-gray-700">Backend Message: {backendMessage}</p>
        </div>
      </div>
      <Testimonials />
    </div>
  );
}
