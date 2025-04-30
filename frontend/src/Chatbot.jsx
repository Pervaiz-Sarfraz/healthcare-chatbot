import { useState, useRef, useEffect } from 'react';
import { 
  processSymptom, 
  getAdditionalSymptoms, 
  processDiagnosis 
} from './api/api';

const Chatbot = () => {
  const [step, setStep] = useState('name');
  const [messages, setMessages] = useState([]);
  const [inputValue, setInputValue] = useState('');
  const [selectedSymptom, setSelectedSymptom] = useState('');
  const [days, setDays] = useState(0);
  const [additionalSymptoms, setAdditionalSymptoms] = useState([]);
  const [symptomOptions, setSymptomOptions] = useState([]);
  const [additionalSymptomOptions, setAdditionalSymptomOptions] = useState([]);
  const chatboxRef = useRef(null);

  // Get CSRF token from meta tag (Django default)
  const getCsrfToken = () => {
    return document.querySelector('[name=csrfmiddlewaretoken]').value;
  };

  // Scroll to bottom of chatbox when messages update
  useEffect(() => {
    if (chatboxRef.current) {
      chatboxRef.current.scrollTop = chatboxRef.current.scrollHeight;
    }
  }, [messages]);

  const addMessage = (text, type) => {
    setMessages(prev => [...prev, { text, type }]);
  };

  const updateInputPlaceholder = (placeholder) => {
    // This will be handled by the input's placeholder prop
  };

  const handleInputChange = (e) => {
    setInputValue(e.target.value);
  };

  const handleSelectChange = (e) => {
    setSelectedSymptom(e.target.value);
  };

  const handleCheckboxChange = (symptom) => {
    setAdditionalSymptoms(prev => 
      prev.includes(symptom)
        ? prev.filter(s => s !== symptom)
        : [...prev, symptom]
    );
  };

  const handleSubmit = async () => {
    const csrfToken = getCsrfToken();
    
    if (step === 'name') {
      if (!inputValue.trim()) {
        alert('Please enter your name.');
        return;
      }
      addMessage(`You: ${inputValue}`, 'user');
      addMessage(`Hello, ${inputValue}! Please enter a symptom you're experiencing.`, 'bot');
      setStep('symptom');
      setInputValue('');
    } 
    else if (step === 'symptom') {
      if (!inputValue.trim()) {
        alert('Please enter a symptom.');
        return;
      }
      addMessage(`You: ${inputValue}`, 'user');
      
      try {
        const data = await processSymptom(inputValue, csrfToken);
        
        if (data.error) {
          addMessage(`Bot: ${data.error}`, 'bot');
          setInputValue('');
          setStep('symptom');
          return;
        }
        
        if (data.matches.length === 1) {
          setSelectedSymptom(data.matches[0]);
          addMessage(`Bot: You mentioned "${data.matches[0]}". For how many days have you had this symptom?`, 'bot');
          setStep('days');
          setInputValue('');
        } else {
          setSymptomOptions(data.matches);
          addMessage('Bot: Please select the most accurate symptom from the list:', 'bot');
          setStep('select_symptom');
        }
      } catch (error) {
        addMessage(`Bot: Error processing symptom: ${error}`, 'bot');
        setInputValue('');
        setStep('symptom');
      }
    } 
    else if (step === 'select_symptom') {
      addMessage(`You: ${selectedSymptom}`, 'user');
      addMessage('Bot: For how many days have you had this symptom?', 'bot');
      setStep('days');
      setInputValue('');
    } 
    else if (step === 'days') {
      const daysValue = parseInt(inputValue);
      if (!daysValue || daysValue <= 0) {
        alert('Please enter a valid number of days.');
        return;
      }
      
      setDays(daysValue);
      addMessage(`You: ${daysValue} days`, 'user');
      
      try {
        const data = await getAdditionalSymptoms(selectedSymptom, csrfToken);
        
        if (data.additional_symptoms && data.additional_symptoms.length > 0) {
          setAdditionalSymptomOptions(data.additional_symptoms);
          addMessage('Bot: Are you experiencing any of these additional symptoms? (Select all that apply)', 'bot');
          setStep('additional_symptoms');
        } else {
          submitDiagnosis();
        }
      } catch (error) {
        addMessage(`Bot: Error fetching additional symptoms: ${error}`, 'bot');
        submitDiagnosis();
      }
    } 
    else if (step === 'additional_symptoms') {
      if (additionalSymptoms.length > 0) {
        additionalSymptoms.forEach(sym => addMessage(`You: ${sym} (yes)`, 'user'));
      } else {
        addMessage('You: No additional symptoms', 'user');
      }
      
      submitDiagnosis();
    }
  };

  const submitDiagnosis = async () => {
    const csrfToken = getCsrfToken();
    const diagnosisData = {
      selectedSymptom,
      days,
      additionalSymptoms
    };
    
    try {
      const data = await processDiagnosis(diagnosisData, csrfToken);
      
      if (data.error) {
        addMessage(`Bot: ${data.error}`, 'bot');
        return;
      }
      
      addMessage(`Bot: Symptoms reported: ${data.symptoms.join(', ')}`, 'bot');
      addMessage(`Bot: ${data.severity}`, 'bot');
      
      if (data.second_disease) {
        addMessage(`Bot: You may have ${data.disease} or ${data.second_disease}`, 'bot');
        addMessage(`Bot: ${data.disease}: ${data.description}`, 'bot');
        addMessage(`Bot: ${data.second_disease}: ${data.second_description}`, 'bot');
      } else {
        addMessage(`Bot: You may have ${data.disease}`, 'bot');
        addMessage(`Bot: ${data.description}`, 'bot');
      }
      
      addMessage('Bot: Recommended precautions:', 'bot');
      data.precautions.forEach((prec, i) => {
        if (prec) addMessage(`Bot: ${i+1}) ${prec}`, 'bot');
      });
      
      setStep('complete');
    } catch (error) {
      addMessage(`Bot: Error processing diagnosis: ${error}`, 'bot');
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const getPlaceholder = () => {
    switch (step) {
      case 'name': return 'Enter your name';
      case 'symptom': return 'Enter a symptom (e.g., fever)';
      case 'days': return 'Enter number of days (e.g., 3)';
      default: return '';
    }
  };

  return (
    <div className="max-w-2xl w-full bg-white rounded-lg shadow-lg p-6">
      <h1 className="text-2xl font-bold text-gray-800 mb-4 text-center">Healthcare Chatbot</h1>
      
      {/* Chatbox */}
      <div 
        ref={chatboxRef}
        className="bg-gray-50 border border-gray-200 rounded-lg p-4 h-96 overflow-y-auto mb-4"
      >
        {messages.map((message, index) => (
          <div 
            key={index}
            className={`message p-2 rounded-lg mb-2 ${
              message.type === 'user' 
                ? 'bg-green-100 text-green-800 ml-auto max-w-xs' 
                : 'bg-blue-100 text-blue-800 max-w-xs'
            }`}
          >
            {message.text}
          </div>
        ))}
      </div>
      
      {/* Input Area */}
      <div className="space-y-4">
        {/* Main text input - shown for name, symptom, days steps */}
        {(step === 'name' || step === 'symptom' || step === 'days') && (
          <div className="flex flex-col">
            <input
              type={step === 'days' ? 'number' : 'text'}
              value={inputValue}
              onChange={handleInputChange}
              onKeyPress={handleKeyPress}
              placeholder={getPlaceholder()}
              className="border border-gray-300 rounded-lg p-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
          </div>
        )}
        
        {/* Symptom select - shown when multiple symptoms match */}
        {step === 'select_symptom' && (
          <div className="flex flex-col">
            <select
              value={selectedSymptom}
              onChange={handleSelectChange}
              className="w-full border border-gray-300 rounded-lg p-2 mb-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              {symptomOptions.map((option, index) => (
                <option key={index} value={option}>{option}</option>
              ))}
            </select>
          </div>
        )}
        
        {/* Checkboxes for additional symptoms */}
        {step === 'additional_symptoms' && (
          <div className="flex flex-col space-y-2">
            {additionalSymptomOptions.map((option, index) => (
              <div key={index} className="flex items-center p-2 rounded bg-gray-50 hover:bg-gray-100">
                <input
                  type="checkbox"
                  id={`sym-${index}`}
                  checked={additionalSymptoms.includes(option)}
                  onChange={() => handleCheckboxChange(option)}
                  className="mr-2"
                />
                <label htmlFor={`sym-${index}`}>{option}</label>
              </div>
            ))}
          </div>
        )}
        
        <div className="flex justify-between">
          {step !== 'complete' ? (
            <button
              onClick={handleSubmit}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition"
            >
              Submit
            </button>
          ) : null}
          
          <button
            onClick={() => window.location.reload()}
            className={`bg-gray-500 text-white px-4 py-2 rounded-lg hover:bg-gray-600 transition ${
              step !== 'complete' ? 'hidden' : ''
            }`}
          >
            Start Over
          </button>
        </div>
      </div>
    </div>
  );
};

export default Chatbot;