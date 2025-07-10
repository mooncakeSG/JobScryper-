"use client";

import { useState } from "react";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { 
  Spinner, 
  PulseLoader, 
  DotsLoader, 
  ProgressBar, 
  Skeleton,
  LoadingOverlay,
  PageLoader 
} from "@/components/ui/loading";
import { 
  FadeIn, 
  SlideIn, 
  ScaleIn, 
  Stagger, 
  Pulse, 
  Bounce, 
  Shake, 
  HoverLift, 
  Ripple 
} from "@/components/ui/animation";
import { 
  CheckCircle, 
  AlertCircle, 
  Info, 
  XCircle,
  Play,
  Pause,
  RotateCcw
} from "lucide-react";

export default function DemoPage() {
  const [progress, setProgress] = useState(0);
  const [loading, setLoading] = useState(false);
  const [showOverlay, setShowOverlay] = useState(false);

  const simulateProgress = () => {
    setProgress(0);
    const interval = setInterval(() => {
      setProgress(prev => {
        if (prev >= 100) {
          clearInterval(interval);
          return 100;
        }
        return prev + 10;
      });
    }, 200);
  };

  const simulateLoading = () => {
    setLoading(true);
    setTimeout(() => setLoading(false), 3000);
  };

  return (
    <div className="space-y-8 p-6">
      <div className="text-center">
        <h1 className="text-4xl font-bold text-gray-900 mb-4">
          Microinteractions Demo
        </h1>
        <p className="text-lg text-gray-600">
          Showcasing smooth animations, loading states, and interactive feedback
        </p>
      </div>

      {/* Loading States */}
      <Card>
        <CardHeader>
          <CardTitle>Loading States & Spinners</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center">
              <Spinner size="sm" />
              <p className="text-sm mt-2">Small Spinner</p>
            </div>
            <div className="text-center">
              <Spinner size="md" variant="primary" />
              <p className="text-sm mt-2">Primary Spinner</p>
            </div>
            <div className="text-center">
              <PulseLoader size="lg" />
              <p className="text-sm mt-2">Pulse Loader</p>
            </div>
            <div className="text-center">
              <DotsLoader />
              <p className="text-sm mt-2">Dots Loader</p>
            </div>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span>Progress Bar</span>
              <Button size="sm" onClick={simulateProgress}>
                <RotateCcw className="h-4 w-4 mr-2" />
                Reset
              </Button>
            </div>
            <ProgressBar value={progress} showLabel />
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <Skeleton variant="text" className="h-4" />
            <Skeleton variant="circular" className="h-12 w-12" />
            <Skeleton variant="rectangular" className="h-20" />
          </div>
        </CardContent>
      </Card>

      {/* Animations */}
      <Card>
        <CardHeader>
          <CardTitle>Animation Components</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <FadeIn delay={0}>
                <Card className="bg-blue-50">
                  <CardContent className="p-4">
                    <p className="text-blue-900">Fade In Animation</p>
                  </CardContent>
                </Card>
              </FadeIn>

              <SlideIn direction="left" delay={200}>
                <Card className="bg-green-50">
                  <CardContent className="p-4">
                    <p className="text-green-900">Slide In from Left</p>
                  </CardContent>
                </Card>
              </SlideIn>

              <ScaleIn delay={400}>
                <Card className="bg-purple-50">
                  <CardContent className="p-4">
                    <p className="text-purple-900">Scale In Animation</p>
                  </CardContent>
                </Card>
              </ScaleIn>
            </div>

            <div className="space-y-4">
              <Pulse>
                <Card className="bg-yellow-50">
                  <CardContent className="p-4">
                    <p className="text-yellow-900">Pulse Animation</p>
                  </CardContent>
                </Card>
              </Pulse>

              <Bounce>
                <Card className="bg-red-50">
                  <CardContent className="p-4">
                    <p className="text-red-900">Bounce Animation</p>
                  </CardContent>
                </Card>
              </Bounce>

              <Shake>
                <Card className="bg-orange-50">
                  <CardContent className="p-4">
                    <p className="text-orange-900">Shake Animation</p>
                  </CardContent>
                </Card>
              </Shake>
            </div>
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-4">Staggered List</h3>
            <Stagger staggerDelay={150}>
              <Card className="mb-2">
                <CardContent className="p-3">
                  <p>Item 1 - Fades in first</p>
                </CardContent>
              </Card>
              <Card className="mb-2">
                <CardContent className="p-3">
                  <p>Item 2 - Fades in second</p>
                </CardContent>
              </Card>
              <Card className="mb-2">
                <CardContent className="p-3">
                  <p>Item 3 - Fades in third</p>
                </CardContent>
              </Card>
            </Stagger>
          </div>
        </CardContent>
      </Card>

      {/* Interactive Elements */}
      <Card>
        <CardHeader>
          <CardTitle>Interactive Feedback</CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="space-y-4">
              <h3 className="font-semibold">Button States</h3>
              <div className="space-y-2">
                <Button loading loadingText="Processing...">
                  Loading Button
                </Button>
                <Button onClick={simulateLoading}>
                  Simulate Loading
                </Button>
                <Ripple>
                  <Button variant="outline">
                    Ripple Effect
                  </Button>
                </Ripple>
              </div>
            </div>

            <div className="space-y-4">
              <h3 className="font-semibold">Hover Effects</h3>
              <div className="grid grid-cols-2 gap-4">
                <HoverLift>
                  <Card className="cursor-pointer">
                    <CardContent className="p-4 text-center">
                      <p>Hover to lift</p>
                    </CardContent>
                  </Card>
                </HoverLift>
                <Card className="cursor-pointer transition-all duration-200 hover:shadow-lg hover:scale-105">
                  <CardContent className="p-4 text-center">
                    <p>Enhanced hover</p>
                  </CardContent>
                </Card>
              </div>
            </div>
          </div>

          <div className="space-y-4">
            <h3 className="font-semibold">Input Interactions</h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              <Input placeholder="Focus me for animation" />
              <Input placeholder="Hover for subtle effect" />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Loading Overlay Demo */}
      <Card>
        <CardHeader>
          <CardTitle>Loading Overlay</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="relative h-40 border rounded-lg">
            <LoadingOverlay 
              loading={showOverlay} 
              text="Processing your request..."
            >
              <div className="p-4">
                <p>This content is behind the loading overlay</p>
                <Button 
                  onClick={() => setShowOverlay(!showOverlay)}
                  className="mt-2"
                >
                  {showOverlay ? 'Hide' : 'Show'} Overlay
                </Button>
              </div>
            </LoadingOverlay>
          </div>
        </CardContent>
      </Card>

      {/* Status Icons */}
      <Card>
        <CardHeader>
          <CardTitle>Status Indicators</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="flex items-center space-x-2 p-3 bg-green-50 rounded-lg">
              <CheckCircle className="h-5 w-5 text-green-600" />
              <span className="text-green-900">Success</span>
            </div>
            <div className="flex items-center space-x-2 p-3 bg-red-50 rounded-lg">
              <XCircle className="h-5 w-5 text-red-600" />
              <span className="text-red-900">Error</span>
            </div>
            <div className="flex items-center space-x-2 p-3 bg-yellow-50 rounded-lg">
              <AlertCircle className="h-5 w-5 text-yellow-600" />
              <span className="text-yellow-900">Warning</span>
            </div>
            <div className="flex items-center space-x-2 p-3 bg-blue-50 rounded-lg">
              <Info className="h-5 w-5 text-blue-600" />
              <span className="text-blue-900">Info</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
} 