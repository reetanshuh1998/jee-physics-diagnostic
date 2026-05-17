"use client";

import { useState, useEffect } from 'react';
import Timer from '@/components/Timer';
import QuestionCard from '@/components/QuestionCard';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import { supabase } from '@/lib/supabase';
import { useRouter } from 'next/navigation';

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function TestPage() {
  const [questions, setQuestions] = useState([]);
  const [currentQuestion, setCurrentQuestion] = useState(0);
  const [selectedAnswers, setSelectedAnswers] = useState({});
  const [markedForReview, setMarkedForReview] = useState([]);
  const [timeLeft, setTimeLeft] = useState(60 * 60); // 1 hour in seconds
  const [loading, setLoading] = useState(true);

  // Auth State
  const [user, setUser] = useState(null);
  const [testAttemptId, setTestAttemptId] = useState(null);
  const router = useRouter();

  // Telemetry State
  const [metrics, setMetrics] = useState({});
  const [visited, setVisited] = useState([0]);
  
  // Results State
  const [results, setResults] = useState(null);
  const [submitting, setSubmitting] = useState(false);
  const [isReviewMode, setIsReviewMode] = useState(false);

  // Check Session on Mount
  useEffect(() => {
    async function checkSession() {
      const { data: { user } } = await supabase.auth.getUser();
      if (!user) {
        router.push('/login');
      } else {
        setUser(user);
        createTestAttempt(user.id);
      }
    }
    checkSession();
  }, [router]);

  const createTestAttempt = async (userId) => {
    try {
      const response = await fetch(`${API_URL}/test-attempts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          user_id: userId,
          test_id: 1, // Hardcoded for now
          status: 'In Progress'
        })
      });
      const data = await response.json();
      setTestAttemptId(data.id);
    } catch (error) {
      console.error("Error creating test attempt:", error);
    }
  };

  // Fetch Questions from Backend
  useEffect(() => {
    async function fetchQuestions() {
      try {
        const response = await fetch(`${API_URL}/questions`);
        const data = await response.json();
        
        // Shuffle questions randomly and take only 30
        const shuffled = data.sort(() => 0.5 - Math.random());
        const selected = shuffled.slice(0, 30);
        
        const parsedQuestions = selected.map((q) => {
          const content = JSON.parse(q.content);
          return {
            id: q.id,
            text: content.text,
            options: content.options,
            correct: parseInt(q.correct_answer),
            chapter: q.chapter,
            topic: q.topic
          };
        });
        
        setQuestions(parsedQuestions);
        
        // Initialize metrics
        const initialMetrics = {};
        parsedQuestions.forEach((_, index) => {
          initialMetrics[index] = { timeSpent: 0, answerChanges: 0, revisits: 0 };
        });
        setMetrics(initialMetrics);
        
        setLoading(false);
      } catch (error) {
        console.error("Error fetching questions:", error);
        setLoading(false);
      }
    }
    
    fetchQuestions();
  }, []);

  // Main Test Timer
  useEffect(() => {
    if (results) return; // Stop timer on submit
    
    const timer = setInterval(() => {
      setTimeLeft((prev) => (prev > 0 ? prev - 1 : 0));
    }, 1000);
    return () => clearInterval(timer);
  }, [results]);

  // Telemetry: Time Spent per Question
  useEffect(() => {
    if (loading || questions.length === 0 || results) return;
    
    const timer = setInterval(() => {
      setMetrics((prev) => ({
        ...prev,
        [currentQuestion]: {
          ...prev[currentQuestion],
          timeSpent: (prev[currentQuestion]?.timeSpent || 0) + 1
        }
      }));
    }, 1000);
    
    return () => clearInterval(timer);
  }, [currentQuestion, loading, questions.length, results]);

  const handleAnswerSelect = (optionIndex) => {
    const isChanging = selectedAnswers[currentQuestion] !== undefined && selectedAnswers[currentQuestion] !== optionIndex;
    
    setSelectedAnswers({
      ...selectedAnswers,
      [currentQuestion]: optionIndex
    });
    
    if (isChanging) {
      setMetrics((prev) => ({
        ...prev,
        [currentQuestion]: {
          ...prev[currentQuestion],
          answerChanges: (prev[currentQuestion]?.answerChanges || 0) + 1
        }
      }));
    }
  };

  const changeQuestion = (newIndex) => {
    if (newIndex === currentQuestion) return;

    // Telemetry: Revisits
    if (visited.includes(newIndex)) {
      setMetrics((prev) => ({
        ...prev,
        [newIndex]: {
          ...prev[newIndex],
          revisits: (prev[newIndex]?.revisits || 0) + 1
        }
      }));
    } else {
      setVisited([...visited, newIndex]);
    }

    setCurrentQuestion(newIndex);
  };

  const saveTelemetry = async () => {
    if (!testAttemptId) return; // Wait for test attempt to be created

    const currentQ = questions[currentQuestion];
    const currentM = metrics[currentQuestion] || { timeSpent: 0, answerChanges: 0, revisits: 0 };
    
    const payload = {
      test_attempt_id: testAttemptId,
      question_id: currentQ.id,
      selected_answer: selectedAnswers[currentQuestion] !== undefined ? selectedAnswers[currentQuestion].toString() : null,
      is_correct: selectedAnswers[currentQuestion] === currentQ.correct,
      time_spent_seconds: currentM.timeSpent,
      revisit_count: currentM.revisits,
      answer_changed: currentM.answerChanges > 0
    };
    
    try {
      await fetch(`${API_URL}/question-attempts`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify(payload)
      });
    } catch (error) {
      console.error("Error saving telemetry:", error);
    }
  };

  const submitTest = async () => {
    setSubmitting(true);
    
    // Save telemetry for current question first
    await saveTelemetry();
    
    let totalScore = 0;
    let correctCount = 0;
    let incorrectCount = 0;
    let unansweredCount = 0;
    const predictions = [];

    for (let i = 0; i < questions.length; i++) {
      const q = questions[i];
      const selected = selectedAnswers[i];
      const m = metrics[i] || { timeSpent: 0, answerChanges: 0, revisits: 0 };
      
      const isCorrect = selected === q.correct;
      
      if (selected === undefined) {
        unansweredCount++;
      } else if (isCorrect) {
        totalScore += 4;
        correctCount++;
      } else {
        totalScore -= 1;
        incorrectCount++;
      }

      // Call AI Prediction for each question
      try {
        const response = await fetch(`${API_URL}/predict-mastery`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            time_spent: m.timeSpent,
            answer_changes: m.answerChanges,
            revisits: m.revisits,
            is_correct: selected !== undefined ? (isCorrect ? 1 : 0) : 0
          })
        });
        const predData = await response.json();
        predictions.push({
          questionIndex: i,
          chapter: q.chapter,
          prediction: predData.prediction,
          probability: predData.probability
        });
      } catch (error) {
        console.error(`Error predicting for question ${i}:`, error);
        predictions.push({
          questionIndex: i,
          chapter: q.chapter,
          prediction: 0,
          probability: 0,
          error: true
        });
      }
    }

    setResults({
      score: totalScore,
      correct: correctCount,
      incorrect: incorrectCount,
      unanswered: unansweredCount,
      predictions: predictions
    });
    setSubmitting(false);
  };

  const toggleMarkForReview = () => {
    if (markedForReview.includes(currentQuestion)) {
      setMarkedForReview(markedForReview.filter((i) => i !== currentQuestion));
    } else {
      setMarkedForReview([...markedForReview, currentQuestion]);
    }
  };

  const clearResponse = () => {
    const newAnswers = { ...selectedAnswers };
    delete newAnswers[currentQuestion];
    setSelectedAnswers(newAnswers);
  };

  if (!user || loading) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center">
        <div className="text-xl font-bold">Loading test environment...</div>
      </div>
    );
  }

  if (questions.length === 0) {
    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex items-center justify-center">
        <div className="text-xl font-bold">No questions available.</div>
      </div>
    );
  }

  const currentMetrics = metrics[currentQuestion] || { timeSpent: 0, answerChanges: 0, revisits: 0 };

  // Results View
  if (results && !isReviewMode) {
    const chartData = results.predictions.map(p => {
      const m = metrics[p.questionIndex] || { timeSpent: 0 };
      return {
        name: `Q${p.questionIndex + 1}`,
        timeSpent: m.timeSpent,
        mastery: p.prediction === 1 ? 'Mastered' : 'Needs Work'
      };
    });

    return (
      <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col p-8">
        <header className="mb-8 flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">Test Results & Diagnostic</h1>
            <p className="text-slate-400">Powered by XGBoost Behavioral Analysis</p>
          </div>
          <button 
            onClick={() => window.location.reload()}
            className="bg-slate-700 hover:bg-slate-600 text-white px-4 py-2 rounded-lg font-medium transition-colors"
          >
            Retake Test
          </button>
        </header>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          {/* Score Card */}
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 flex flex-col justify-between">
            <div>
              <h2 className="text-lg font-bold text-slate-400 mb-2">Total Score</h2>
              <p className="text-5xl font-extrabold text-indigo-400">{results.score}<span className="text-2xl text-slate-600">/{questions.length * 4}</span></p>
            </div>
            <div className="mt-4 flex justify-between text-sm">
              <span className="text-emerald-500">Correct: {results.correct}</span>
              <span className="text-red-500">Incorrect: {results.incorrect}</span>
              <span className="text-slate-500">Left: {results.unanswered}</span>
            </div>
          </div>

          {/* AI Insights Summary */}
          <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 md:col-span-2">
            <h2 className="text-lg font-bold text-indigo-400 mb-4">AI Diagnostic Insights</h2>
            <div className="space-y-3">
              {results.predictions.map((p, i) => (
                <div key={i} className="flex justify-between items-center bg-slate-750 p-3 rounded-lg">
                  <div>
                    <span className="font-medium">Q{p.questionIndex + 1} ({p.chapter})</span>
                    {p.error && <span className="text-xs text-red-500 ml-2">(Pred Error)</span>}
                  </div>
                  <div className={`px-3 py-1 rounded-full text-xs font-bold ${
                    p.prediction === 1 ? 'bg-emerald-600/20 text-emerald-400' : 'bg-yellow-600/20 text-yellow-400'
                  }`}>
                    {p.prediction === 1 ? 'Mastered' : 'Needs Work'} ({(p.probability * 100).toFixed(0)}%)
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Chart Card */}
        <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 mt-6">
          <h2 className="text-lg font-bold text-indigo-400 mb-4">Time Spent per Question (Seconds)</h2>
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="name" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" />
                <Tooltip 
                  contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #475569', borderRadius: '0.5rem' }}
                  labelStyle={{ color: '#f8fafc' }}
                  itemStyle={{ color: '#6366f1' }}
                />
                <Bar dataKey="timeSpent" fill="#6366f1" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="mt-8 text-center flex gap-4 justify-center">
          <button 
            onClick={() => setIsReviewMode(true)}
            className="bg-indigo-600 hover:bg-indigo-700 text-white px-6 py-3 rounded-lg font-medium transition-colors"
          >
            Review Answers
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-slate-900 text-slate-100 flex flex-col">
      {/* Header */}
      <header className="bg-slate-800 border-b border-slate-700 p-4 flex justify-between items-center backdrop-blur-md bg-opacity-70 sticky top-0 z-10">
        <div>
          <h1 className="text-xl font-bold bg-gradient-to-r from-violet-400 to-indigo-400 bg-clip-text text-transparent">JEE Physics Diagnostic</h1>
          <p className="text-sm text-slate-400">Chapter: {questions[currentQuestion].chapter}</p>
        </div>
        <div className="flex items-center gap-4">
          {!results && <Timer timeLeft={timeLeft} />}
          {results && isReviewMode ? (
            <button 
              onClick={() => setIsReviewMode(false)}
              className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-medium transition-colors"
            >
              Back to Results
            </button>
          ) : (
            <button 
              onClick={submitTest}
              disabled={submitting}
              className="bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg font-medium transition-colors disabled:opacity-50"
            >
              {submitting ? 'Submitting...' : 'Submit Test'}
            </button>
          )}
        </div>
      </header>

      {/* Main Content */}
      <div className="flex-1 flex flex-col md:flex-row">
        {/* Question Area */}
        <div className="flex-1 p-6 flex flex-col justify-between">
          <QuestionCard 
            question={questions[currentQuestion]}
            currentQuestionIndex={currentQuestion}
            totalQuestions={questions.length}
            selectedAnswer={selectedAnswers[currentQuestion]}
            onAnswerSelect={handleAnswerSelect}
            isReviewMode={isReviewMode}
          />

          {/* Action Buttons */}
          <div className="flex flex-wrap justify-between items-center mt-8 pt-4 border-t border-slate-800 gap-3">
            <div className="flex gap-3">
              {!isReviewMode && (
                <>
                  <button 
                    onClick={clearResponse}
                    className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-sm font-medium"
                  >
                    Clear Response
                  </button>
                  <button 
                    onClick={toggleMarkForReview}
                    className={`px-5 py-2.5 rounded-lg transition-colors text-sm font-medium ${
                      markedForReview.includes(currentQuestion)
                        ? 'bg-yellow-600 hover:bg-yellow-700 text-white'
                        : 'bg-slate-700 hover:bg-slate-600'
                    }`}
                  >
                    {markedForReview.includes(currentQuestion) ? 'Marked' : 'Mark for Review'}
                  </button>
                </>
              )}
            </div>
            <div className="flex gap-3">
              <button 
                onClick={() => changeQuestion(Math.max(0, currentQuestion - 1))}
                className="px-5 py-2.5 bg-slate-700 hover:bg-slate-600 rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
                disabled={currentQuestion === 0}
              >
                Previous
              </button>
              <button 
                onClick={async () => {
                  if (!isReviewMode) await saveTelemetry();
                  changeQuestion(Math.min(questions.length - 1, currentQuestion + 1));
                }}
                className="px-5 py-2.5 bg-indigo-600 hover:bg-indigo-700 rounded-lg transition-colors text-sm font-medium disabled:opacity-50"
                disabled={currentQuestion === questions.length - 1}
              >
                {isReviewMode ? 'Next' : 'Save & Next'}
              </button>
            </div>
          </div>
        </div>

        {/* Sidebar */}
        <div className="w-full md:w-80 bg-slate-850 border-l border-slate-700 p-6 flex flex-col justify-between">
          <div>
            <h2 className="text-lg font-bold mb-4">Question Palette</h2>
            <div className="grid grid-cols-4 gap-3">
              {questions.map((q, index) => {
                let statusClass = "bg-slate-700 border-slate-600";
                if (currentQuestion === index) {
                  statusClass = "border-indigo-500 ring-2 ring-indigo-500 ring-opacity-50";
                } else if (!isReviewMode && markedForReview.includes(index)) {
                  statusClass = "bg-yellow-600 border-yellow-500";
                } else if (selectedAnswers[index] !== undefined) {
                  if (isReviewMode) {
                    const isCorrect = selectedAnswers[index] === q.correct;
                    statusClass = isCorrect ? "bg-emerald-600 border-emerald-500" : "bg-red-600 border-red-500";
                  } else {
                    statusClass = "bg-emerald-600 border-emerald-500";
                  }
                }
                
                return (
                  <div 
                    key={index}
                    onClick={() => changeQuestion(index)}
                    className={`w-12 h-12 flex items-center justify-center rounded-lg border cursor-pointer font-medium transition-all ${statusClass}`}
                  >
                    {index + 1}
                  </div>
                );
              })}
            </div>

            {/* Legend */}
            <div className="mt-8 space-y-3 text-sm">
              {isReviewMode ? (
                <>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-emerald-600 rounded"></div>
                    <span>Correct</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-red-600 rounded"></div>
                    <span>Incorrect</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-slate-700 rounded"></div>
                    <span>Not Answered</span>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-emerald-600 rounded"></div>
                    <span>Answered</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-yellow-600 rounded"></div>
                    <span>Marked for Review</span>
                  </div>
                  <div className="flex items-center gap-3">
                    <div className="w-4 h-4 bg-slate-700 rounded"></div>
                    <span>Not Answered</span>
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Telemetry Debug Info */}
          <div className="mt-8 p-4 bg-slate-800 rounded-lg border border-slate-700">
            <h3 className="font-bold mb-2 text-indigo-400">Student Profile (Debug)</h3>
            <div className="space-y-1 text-sm">
              <p><span className="text-slate-400">Time Spent:</span> {currentMetrics.timeSpent}s</p>
              <p><span className="text-slate-400">Answer Changes:</span> {currentMetrics.answerChanges}</p>
              <p><span className="text-slate-400">Revisits:</span> {currentMetrics.revisits}</p>
            </div>
            <p className="text-xs text-slate-500 mt-2">These metrics will be sent to the XGBoost model.</p>
          </div>
        </div>
      </div>
    </div>
  );
}
