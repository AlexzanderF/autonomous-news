'use client';

import AdPlaceholder from '@/components/AdPlaceholder';

export default function EconomicCalendarPage() {

    return (
        <div className="min-h-screen pt-28 pb-12 px-4 md:px-8">
            <div className="max-w-7xl mx-auto">

                <div className="grid grid-cols-1 lg:grid-cols-12 gap-12">
                    <div className="lg:col-span-8">
                        <header className="mt-12 mb-8 border-b border-slate-200 pb-8">
                            <h1 className="text-4xl md:text-5xl text-slate-900 leading-tight font-sans">
                                Economic Calendar
                            </h1>
                        </header>

                        <div className="calendar-widget">
                            <iframe
                                src="https://sslecal2.investing.com?columns=exc_flags,exc_currency,exc_importance,exc_actual,exc_forecast,exc_previous&features=datepicker,timezone,filters&countries=25,32,6,37,72,22,17,39,14,10,35,43,56,36,110,11,26,12,4,5&calType=week&timeZone=8&lang=1&width=650"
                                className="w-full"
                                height="467"
                                frameBorder="0"
                            />
                            <div className="font-sans mt-2">
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
