'use client'

import React, { useEffect, useState } from 'react';
import Testimonials from '@/components/pages/home/Testimonials'
import Hero from '@/components/pages/home/Hero'

export default function Home() {
  const [backendMessage, setBackendMessage] = useState("");

  useEffect(() => {
    fetch("http://127.0.0.1:8000/test/")
      .then((response) => response.json())
      .then((data) => setBackendMessage(data.message))
      .catch((error) => console.error("Error fetching from backend:", error));
  }, []);

  return (
    <div className="ml-[3%] mr-[3%]">
      <Hero />
      <Testimonials />
    </div>
  );
}
