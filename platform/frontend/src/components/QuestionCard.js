export default function QuestionCard({ 
  question, 
  currentQuestionIndex, 
  totalQuestions, 
  selectedAnswer, 
  onAnswerSelect,
  isReviewMode = false
}) {
  const isCorrect = selectedAnswer === question.correct;
  
  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <span className="text-sm font-medium text-indigo-400 uppercase tracking-wider">
          Question {currentQuestionIndex + 1} of {totalQuestions}
        </span>
        <span className="text-sm text-slate-400">Marks: +4 / -1</span>
      </div>

      <div className="bg-slate-800 p-6 rounded-xl border border-slate-700 shadow-xl mb-6">
        <p className="text-lg leading-relaxed">{question.text}</p>
      </div>

      <div className="space-y-3">
        {question.options.map((option, index) => {
          let borderClass = 'border-slate-700 bg-slate-800 hover:border-slate-600 hover:bg-slate-750';
          let radioBorderClass = 'border-slate-500';
          let radioFillClass = 'bg-white';

          if (isReviewMode) {
            if (index === question.correct) {
              borderClass = 'border-emerald-500 bg-emerald-900 bg-opacity-30';
              radioBorderClass = 'border-emerald-500 bg-emerald-500';
            } else if (selectedAnswer === index && !isCorrect) {
              borderClass = 'border-red-500 bg-red-900 bg-opacity-30';
              radioBorderClass = 'border-red-500 bg-red-500';
            }
          } else {
            if (selectedAnswer === index) {
              borderClass = 'border-indigo-500 bg-indigo-900 bg-opacity-30';
              radioBorderClass = 'border-indigo-500 bg-indigo-500';
            }
          }

          return (
            <div 
              key={index}
              onClick={() => !isReviewMode && onAnswerSelect(index)}
              className={`p-4 rounded-lg border transition-all ${
                !isReviewMode ? 'cursor-pointer' : 'cursor-default'
              } ${borderClass}`}
            >
              <div className="flex items-center gap-3">
                <div className={`w-5 h-5 rounded-full border flex items-center justify-center ${radioBorderClass}`}>
                  {(selectedAnswer === index || (isReviewMode && index === question.correct)) && (
                    <div className={`w-2 h-2 rounded-full ${radioFillClass}`}></div>
                  )}
                </div>
                <span>{option}</span>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
