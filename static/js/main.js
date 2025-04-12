document.addEventListener('DOMContentLoaded', () => {
    let selectedMood = null;
    const moodButtons = document.querySelectorAll('#mood-buttons button');
    const noteTextarea = document.getElementById('mood-note');
    const saveButton = document.getElementById('save-mood');

    moodButtons.forEach(button => {
        button.addEventListener('click', () => {
            // Remove active state from all buttons
            moodButtons.forEach(btn => {
                btn.classList.remove('bg-blue-100', 'scale-110');
                btn.classList.add('hover:bg-gray-100');
            });

            // Add active state to clicked button
            button.classList.add('bg-blue-100', 'scale-110');
            button.classList.remove('hover:bg-gray-100');
            
            selectedMood = button.dataset.mood;
            
            // Enable save button
            saveButton.disabled = false;
            saveButton.classList.remove('bg-gray-200', 'text-gray-500', 'cursor-not-allowed');
            saveButton.classList.add('bg-blue-500', 'text-white', 'hover:bg-blue-600');
        });
    });

    saveButton.addEventListener('click', async () => {
        if (!selectedMood) return;

        try {
            const response = await fetch('/api/mood', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    mood: selectedMood,
                    note: noteTextarea.value
                })
            });

            if (response.ok) {
                // Reset form
                selectedMood = null;
                noteTextarea.value = '';
                moodButtons.forEach(btn => {
                    btn.classList.remove('bg-blue-100', 'scale-110');
                    btn.classList.add('hover:bg-gray-100');
                });
                saveButton.disabled = true;
                saveButton.classList.add('bg-gray-200', 'text-gray-500', 'cursor-not-allowed');
                saveButton.classList.remove('bg-blue-500', 'text-white', 'hover:bg-blue-600');

                // Reload page to show new entry
                window.location.reload();
            }
        } catch (error) {
            console.error('Error saving mood:', error);
        }
    });
});