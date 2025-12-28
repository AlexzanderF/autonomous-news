'use client';

import { useMemo, useState } from 'react';
import AdPlaceholder from '@/components/AdPlaceholder';

export default function EconomicCalendarPage() {
    const [isLoading, setIsLoading] = useState(true);

    // Investing.com timezone mapping:
    // The timeZone parameter uses specific IDs. Common ones:
    // 8 = GMT+8, 15 = GMT+2 (Eastern European), 55 = UTC, etc.
    // We'll map the browser's offset to the closest available timezone
    const iframeSrc = useMemo(() => {
        const offsetMinutes = new Date().getTimezoneOffset();
        const offsetHours = -offsetMinutes / 60; // Convert to hours (negative because getTimezoneOffset returns opposite)
        
        // Investing.com timezone IDs follow a simple formula:
        // 15 = UTC/GMT, and each hour offset adds/subtracts 1
        // e.g., GMT+2 = 17, GMT-5 = 10
        const timezoneId = 15 + Math.round(offsetHours);
        
        return `https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timezone,filters&countries=25,32,6,37,72,22,17,39,14,10,35,43,56,36,110,11,26,12,4,5&calType=week&timeZone=${timezoneId}&lang=1`;
    }, []);

    return (
        <div className="h-[calc(100vh-104px)] pt-28 pb-4 flex flex-col">
            <div className="w-full flex-1 flex flex-col min-h-0">

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 flex-1 min-h-0">
                    <div className="lg:col-span-8 flex flex-col min-h-0">
                        <header className="mt-12 mb-8 border-b border-slate-200 pb-8 flex-shrink-0">
                            <h1 className="text-4xl md:text-5xl text-slate-900 leading-tight font-sans">
                                Economic Calendar
                            </h1>
                        </header>

                        <div className="calendar-widget flex-1 min-h-0 flex flex-col relative">
                            {isLoading && (
                                <div className="absolute inset-0 flex items-center justify-center bg-white z-10">
                                    <div className="flex flex-col items-center gap-3">
                                        <div className="w-10 h-10 border-4 border-slate-200 border-t-blue-600 rounded-full animate-spin"></div>
                                        <span className="text-slate-500 text-sm font-sans">Loading calendar...</span>
                                    </div>
                                </div>
                            )}
                            <iframe
                                src={iframeSrc}
                                className="w-full flex-1"
                                width="100%"
                                frameBorder="0"
                                onLoad={() => setIsLoading(false)}
                            />
                        </div>
                        <div className="font-sans mt-2 flex-shrink-0">
                            <span className="text-[11px] text-slate-700 no-underline">
                                Real Time Economic Calendar provided by{' '}
                                <a
                                    href="https://www.investing.com/"
                                    rel="nofollow"
                                    target="_blank"
                                    className="text-[11px] text-blue-700 font-bold hover:underline"
                                >
                                    Investing.com
                                </a>
                                .
                            </span>
                        </div>
                    </div>

                    <div className="lg:col-span-4">
                        <div className="sticky top-24 mt-12 space-y-6">
                            {/* Advertisement */}
                            <AdPlaceholder width={250} height={600} />
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
