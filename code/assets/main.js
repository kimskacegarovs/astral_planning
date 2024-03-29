function getMergedFormsData(formIds) {
    const result = {};
    for (const formId of formIds) {
        const form = document.getElementById(formId);
        const formData = new FormData(form);
        for (const [key, value] of formData.entries()) result[key] = value;
    }
    return result;
}