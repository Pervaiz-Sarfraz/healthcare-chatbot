import axiosInstance from "./axiosInstance";

// Healthcare Chatbot Endpoints
export const processSymptom = async (symptom, csrfToken) => {
  const formData = new URLSearchParams();
  formData.append('symptom', symptom);
  
  return axiosInstance.post('/chatdoctor/process_symptom/', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken
    }
  });
};

export const getAdditionalSymptoms = async (selectedSymptom, csrfToken) => {
  const formData = new URLSearchParams();
  formData.append('selected_symptom', selectedSymptom);
  
  return axiosInstance.post('/chatdoctor/get_additional_symptoms/', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken
    }
  });
};

export const processDiagnosis = async (diagnosisData, csrfToken) => {
  const formData = new URLSearchParams();
  formData.append('selected_symptom', diagnosisData.selectedSymptom);
  formData.append('days', diagnosisData.days);
  diagnosisData.additionalSymptoms.forEach(sym => 
    formData.append('additional_symptoms', sym)
  );

  return axiosInstance.post('/chatdoctor/process_diagnosis/', formData, {
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
      'X-CSRFToken': csrfToken
    }
  });
};


// Authentication Endpoints
export const register = (email, password) =>
  axiosInstance.post('/register/', { email, password });

export const login = (email, password) =>
  axiosInstance.post('/login/', { email, password });

export const logout = () =>
  axiosInstance.post('/logout/');

export const getCurrentUser = () =>
  axiosInstance.get('/users/me/');



// Job Portal Endpoints
// export const fetchCompanies = () => 
//   axiosInstance.get('/companies/');

// export const fetchJobs = () => 
//   axiosInstance.get('/jobs/');

// export const fetchJobById = (id) => 
//   axiosInstance.get(`/jobs/${id}/`);

// export const createCompany = (companyData) =>
//   axiosInstance.post('/companies/', companyData, {
//     headers: { "Content-Type": "multipart/form-data" }
//   });

// export const createJob = (jobData) =>
//   axiosInstance.post('/jobs/', jobData);

// export const applyToJob = (applicationData) =>
//   axiosInstance.post('/applications/', applicationData, {
//     headers: { "Content-Type": "multipart/form-data" }
//   });