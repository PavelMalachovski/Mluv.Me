"use client"

import { useState, useEffect, useRef } from "react"
import { useReactMediaRecorder } from "react-media-recorder"
import { Mic, Square, Loader2, Send, X } from "lucide-react"
import { Button } from "./button"

interface VoiceRecorderProps {
    onRecordComplete: (audioBlob: Blob) => void
    isProcessing?: boolean
    maxDurationSeconds?: number
}

export function VoiceRecorder({
    onRecordComplete,
    isProcessing = false,
    maxDurationSeconds = 60
}: VoiceRecorderProps) {
    const [recordingDuration, setRecordingDuration] = useState(0)
    const timerRef = useRef<NodeJS.Timeout | null>(null)
    const [audioUrl, setAudioUrl] = useState<string | null>(null)

    const {
        status,
        startRecording,
        stopRecording,
        mediaBlobUrl,
        clearBlobUrl,
    } = useReactMediaRecorder({
        audio: true,
        mediaRecorderOptions: {
            mimeType: "audio/webm;codecs=opus",
        },
        onStop: (blobUrl, blob) => {
            setAudioUrl(blobUrl)
        },
    })

    // Handle recording duration timer
    useEffect(() => {
        if (status === "recording") {
            setRecordingDuration(0)
            timerRef.current = setInterval(() => {
                setRecordingDuration((prev) => {
                    if (prev >= maxDurationSeconds - 1) {
                        stopRecording()
                        return prev
                    }
                    return prev + 1
                })
            }, 1000)
        } else {
            if (timerRef.current) {
                clearInterval(timerRef.current)
                timerRef.current = null
            }
        }

        return () => {
            if (timerRef.current) {
                clearInterval(timerRef.current)
            }
        }
    }, [status, maxDurationSeconds, stopRecording])

    const formatTime = (seconds: number) => {
        const mins = Math.floor(seconds / 60)
        const secs = seconds % 60
        return `${mins}:${secs.toString().padStart(2, "0")}`
    }

    const handleSend = async () => {
        if (mediaBlobUrl) {
            try {
                const response = await fetch(mediaBlobUrl)
                const blob = await response.blob()
                onRecordComplete(blob)
                clearBlobUrl()
                setAudioUrl(null)
                setRecordingDuration(0)
            } catch (error) {
                console.error("Error getting audio blob:", error)
            }
        }
    }

    const handleCancel = () => {
        clearBlobUrl()
        setAudioUrl(null)
        setRecordingDuration(0)
    }

    const isRecording = status === "recording"
    const hasRecording = mediaBlobUrl && status === "stopped"

    return (
        <div className="flex items-center gap-3">
            {/* Recording state */}
            {isRecording && (
                <div className="flex items-center gap-3 flex-1">
                    {/* Waveform animation */}
                    <div className="flex items-center gap-1 h-8">
                        {[...Array(5)].map((_, i) => (
                            <div
                                key={i}
                                className="w-1 bg-red-500 rounded-full animate-pulse"
                                style={{
                                    height: `${Math.random() * 100}%`,
                                    minHeight: "8px",
                                    animationDelay: `${i * 0.1}s`,
                                    animationDuration: "0.5s",
                                }}
                            />
                        ))}
                    </div>

                    {/* Duration */}
                    <span className="text-sm font-mono text-red-500 min-w-[48px]">
                        {formatTime(recordingDuration)}
                    </span>

                    {/* Max duration indicator */}
                    <span className="text-xs text-muted-foreground">
                        / {formatTime(maxDurationSeconds)}
                    </span>
                </div>
            )}

            {/* Playback state */}
            {hasRecording && !isProcessing && (
                <div className="flex items-center gap-3 flex-1">
                    <audio src={audioUrl || undefined} controls className="h-10 flex-1" />
                </div>
            )}

            {/* Processing state */}
            {isProcessing && (
                <div className="flex items-center gap-2 flex-1">
                    <Loader2 className="h-5 w-5 animate-spin text-primary" />
                    <span className="text-sm text-muted-foreground">Processing...</span>
                </div>
            )}

            {/* Action buttons */}
            <div className="flex items-center gap-2">
                {/* Record button */}
                {!isRecording && !hasRecording && !isProcessing && (
                    <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={startRecording}
                        className="h-12 w-12 rounded-full bg-red-500 hover:bg-red-600 text-white border-0"
                    >
                        <Mic className="h-6 w-6" />
                    </Button>
                )}

                {/* Stop button */}
                {isRecording && (
                    <Button
                        type="button"
                        variant="outline"
                        size="icon"
                        onClick={stopRecording}
                        className="h-12 w-12 rounded-full bg-gray-800 hover:bg-gray-900 text-white border-0"
                    >
                        <Square className="h-5 w-5" />
                    </Button>
                )}

                {/* Send/Cancel buttons for recorded audio */}
                {hasRecording && !isProcessing && (
                    <>
                        <Button
                            type="button"
                            variant="outline"
                            size="icon"
                            onClick={handleCancel}
                            className="h-10 w-10 rounded-full"
                        >
                            <X className="h-5 w-5" />
                        </Button>
                        <Button
                            type="button"
                            size="icon"
                            onClick={handleSend}
                            className="h-12 w-12 rounded-full bg-primary hover:bg-primary/90"
                        >
                            <Send className="h-5 w-5" />
                        </Button>
                    </>
                )}
            </div>
        </div>
    )
}
