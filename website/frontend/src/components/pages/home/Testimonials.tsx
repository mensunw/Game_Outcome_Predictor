import { cn } from '@/lib/utils'
import Marquee from '@/components/ui/marquee'
import { Card, CardHeader, CardFooter, CardTitle, CardDescription, CardContent } from '@/components/ui/card'
import { Button } from '@/components/ui/button'

const reviews = [
    {
        name: 'Jack',
        username: '@jack',
        body: "I've never seen anything like this before. It's amazing. I love it.",
        img: 'https://avatar.vercel.sh/jack',
    },
    {
        name: 'Jill',
        username: '@jill',
        body: "I don't know what to say. I'm speechless. This is amazing.",
        img: 'https://avatar.vercel.sh/jill',
    },
    {
        name: 'John',
        username: '@john',
        body: "I'm at a loss for words. This is amazing. I love it.",
        img: 'https://avatar.vercel.sh/john',
    },
    {
        name: 'Jane',
        username: '@jane',
        body: "I'm at a loss for words. This is amazing. I love it.",
        img: 'https://avatar.vercel.sh/jane',
    },
    {
        name: 'Jenny',
        username: '@jenny',
        body: "I'm at a loss for words. This is amazing. I love it.",
        img: 'https://avatar.vercel.sh/jenny',
    },
    {
        name: 'James',
        username: '@james',
        body: "I'm at a loss for words. This is amazing. I love it.",
        img: 'https://avatar.vercel.sh/james',
    },
]

const firstRow = reviews.slice(0, reviews.length / 2)
const secondRow = reviews.slice(reviews.length / 2)

const ReviewCard = ({
    img,
    name,
    username,
    body,
}: {
    img: string
    name: string
    username: string
    body: string
}) => {
    const handleClick = () => {
        // Programmatically announce content for screen readers
        const announcement = `${name}, username ${username}: ${body}`;
        const liveRegion = document.getElementById('live-region');
        if (liveRegion) {
            liveRegion.textContent = announcement;

            // Clear the content after announcement to avoid conflicts
            setTimeout(() => {
                liveRegion.textContent = '';
            }, 1000);
        }
    };

    return (
        <figure
            className={cn(
                'relative w-64 cursor-pointer overflow-hidden rounded-xl border p-4',
                'border-gray-950/[.1] bg-gray-950/[.01] hover:bg-gray-950/[.05]',
                'dark:border-gray-50/[.1] dark:bg-gray-50/[.10] dark:hover:bg-gray-50/[.15]'
            )}
            tabIndex={0} // Makes the card focusable for keyboard navigation
            aria-labelledby={`review-${username}`} // Links to descriptive content for screen readers
            onClick={handleClick} // Announces content for screen readers
        >
            <div className="flex flex-row items-center gap-2">
                <img
                    className="rounded-full"
                    width="32"
                    height="32"
                    alt={`${name}'s avatar`}
                    src={img}
                />
                <div className="flex flex-col">
                    <figcaption
                        id={`review-${username}`}
                        className="text-sm font-medium dark:text-white"
                    >
                        {name}
                    </figcaption>
                    <p className="text-xs font-medium dark:text-white/40">{username}</p>
                </div>
            </div>
            <blockquote className="mt-2 text-sm">{body}</blockquote>
        </figure>
    )
}

export default function Testimonials() {
    return (
        <Card className="bg-sky-100 ml-[18%] mr-[18%] mt-[5%]">
            <section className="container mx-auto px-4 py-12 text-center">
                {/* Title and Description */}
                <div className="mb-8 flex flex-col items-center">
                    <h2 className="text-3xl font-bold tracking-tight">
                        Optimize Your Gameplay with the FF Detector
                    </h2>
                    <p className="mt-2 w-3/4 text-lg text-muted-foreground">
                        Effortlessly predict your game’s outcome within the first 15 minutes and make informed decisions to surrender or keep pushing for victory.
                    </p>
                </div>

                {/* Live Region for Screen Readers */}
                <div
                    id="live-region"
                    aria-live="polite"
                    aria-atomic="true"
                    className="sr-only"
                ></div>

                {/* Testimonials Section */}
                <div className="relative">
                    <Marquee
                        pauseOnHover
                        className="[--duration:20s]"
                        aria-live="polite" // Ensures testimonials are announced as they scroll
                    >
                        {firstRow.map((review) => (
                            <ReviewCard key={review.username} {...review} />
                        ))}
                    </Marquee>
                    <Marquee
                        reverse
                        pauseOnHover
                        className="[--duration:20s]"
                        aria-live="polite"
                    >
                        {secondRow.map((review) => (
                            <ReviewCard key={review.username} {...review} />
                        ))}
                    </Marquee>
                    {/* Gradient Overlays */}
                    <div className="pointer-events-none absolute inset-y-0 left-0 w-1/3 bg-gradient-to-r from-background"></div>
                    <div className="pointer-events-none absolute inset-y-0 right-0 w-1/3 bg-gradient-to-l from-background"></div>
                </div>
                {/* Get Started Section */}
                <div className="mb-8 flex flex-col items-center">
                    <h2 className="text-3xl font-bold tracking-tight">
                        Unlock the Power of Precision
                    </h2>
                    <p className="mt-2 w-3/4 text-lg text-muted-foreground">
                        Ready to level up your gameplay? Discover the FF Detector, your ultimate tool for predicting game outcomes with unmatched accuracy!
                    </p>

                    <Button> Get Started For Free > </Button>
                </div>
            </section>
        </Card>
    )
}