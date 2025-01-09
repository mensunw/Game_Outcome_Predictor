'use client'

import React, { useEffect, useState } from 'react';
import Testimonials from '@/components/pages/home/Testimonials'
import Hero from '@/components/pages/home/Hero'

export default function Home() {
  const [backendMessage, setBackendMessage] = useState("");

  return (
    <div className="" >
      <Hero />
      <Testimonials />
    </div>
  );
}
