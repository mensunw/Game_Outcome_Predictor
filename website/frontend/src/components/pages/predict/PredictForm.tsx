"use client"

import { zodResolver } from "@hookform/resolvers/zod"
import { useForm } from "react-hook-form"
import { z } from "zod"

import { Button } from "@/components/ui/button"
import {
    Form,
    FormControl,
    FormDescription,
    FormField,
    FormItem,
    FormLabel,
    FormMessage,
} from "@/components/ui/form"
import { Input } from "@/components/ui/input"
import { useToast } from '@/hooks/use-toast'
import { useEffect, useState } from 'react'
import { useRouter } from 'next/navigation'

const formSchema = z.object({
    username: z.string().min(2, {
        message: "must be at least 2 characters.",
    }),
})

export default function ProfileForm() {

    const { toast } = useToast()
    const router = useRouter()

    // 1. Define your form.
    const form = useForm<z.infer<typeof formSchema>>({
        resolver: zodResolver(formSchema),
        defaultValues: {
            username: "",
        },
    })

    // 2. Define a submit handler.
    async function onSubmit(values: z.infer<typeof formSchema>) {
        // Call backend to check and predict the outcome using the model
        try {
            const response = await (
                await fetch("http://127.0.0.1:8000/predict/",
                    {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify(values),
                    })
            ).json()
            const { result, error } = response

            if (result || result == false) {
                const queryString = `data=${encodeURIComponent(result)}`;
                router.push(`/predict/result?${queryString}`);
            }

            if (error) {
                toast({
                    variant: "destructive",
                    title: "Invalid request",
                    description: error,
                })
            }


        } catch (error) {
            toast({
                variant: "destructive",
                title: "Uh oh! Something went wrong.",
                description: "There was a problem with your request.",
            })
            console.error("Error fetching from backend:", error);
        }
    }

    return (
        <Form {...form}>
            <form onSubmit={form.handleSubmit(onSubmit)} className="flex flex-row justify-center gap-2">
                <FormField
                    control={form.control}
                    name="username"
                    render={({ field }) => (
                        <FormItem>
                            <FormControl>
                                <Input placeholder="Game Name + Tag Line" {...field} className="w-96" />
                            </FormControl>
                            <FormDescription>
                                *please ensure your game has just started
                            </FormDescription>
                            <FormMessage />
                        </FormItem>
                    )}
                />
                <Button type="submit">Predict</Button>
            </form>
        </Form>
    )
}
