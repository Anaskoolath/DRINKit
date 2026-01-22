// Download CV functionality
function downloadCV() {
    const element = document.getElementById('cvSection');
    html2pdf()
        .from(element)
        .save("My_CV.pdf");
}

// Form submission handler
function handleSubmit(e) {
    e.preventDefault();
    const form = e.target;
    const name = form.name.value.trim();
    const email = form.email.value.trim();
    const message = form.message.value.trim();
    const status = document.getElementById('formStatus');
    
    if (!name || !email || !message) {
        status.textContent = 'Please fill all fields.';
        status.className = 'mt-3 text-sm text-red-500';
        return;
    }
    
    status.textContent = `Thanks, ${name}! I will contact you at ${email}.`;
    status.className = 'mt-3 text-sm text-green-600';
    form.reset();
}
