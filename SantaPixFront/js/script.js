let qrCodeElement = document.querySelector('.qr-code');
let buttonGenerateQr = document.querySelector('.generate-pix');
let form = document.querySelector('.form');
let inputValor = document.querySelector('.value');
let sectionGerarPix = document.querySelector('.container__gerar__pix');
let sectionQrCode = document.querySelector('.container__qrcode');
let paidStatus = document.querySelector('.paid');
let newQrCode = document.querySelector('.new__qr');

const API_URL = "http://10.220.0.6:5000";

inputValor.addEventListener('input', (event) => {
    const value = event.target.value;

    if (value.length > 0) {
        buttonGenerateQr.disabled = false;
    } else {
        buttonGenerateQr.disabled = true;
    }

   // Mascara para o campo de valor
    event.target.value = "R$ " + value.replace(/\D/g, "")
        .replace(/(\d{1})(\d{14})$/, "$1.$2")
        .replace(/(\d{1})(\d{11})$/, "$1.$2")
        .replace(/(\d{1})(\d{8})$/, "$1.$2")
        .replace(/(\d{1})(\d{5})$/, "$1.$2")
        .replace(/(\d{1})(\d{1,2})$/, "$1,$2");
});

// Pegando os valores do formulário
form.addEventListener('submit', async (event) => {
    event.preventDefault();

    const value = inputValor.value;
    const solicitacao_pagador = document.querySelector('.description').value;

    // Removendo o R$ do valor e a máscara, deixando exemplo: 1100.00
    const valueWithoutMask = value.replace('R$ ', '').replace('.', '').replace(',', '.');

    const data = await generatePix(valueWithoutMask, solicitacao_pagador);
    const txId = data.data.txid;

    const response = await fetch(API_URL + "/pix/qr/" + txId, {
        method: 'GET'
    });

    const dataResponse = await response.json();

    generateQrCode(dataResponse.data);

    sectionGerarPix.classList.add('none');
    sectionQrCode.classList.add('show');

    // Verifica se o pix foi pago durante 5 minutos
    const time = new Date().getTime();
    const interval = setInterval(async () => {
        const timeNow = new Date().getTime();
        const isPaid = await checkPix(txId);
        if (isPaid) {
            setTimeout(() => {
                paidStatus.classList.add('success');
                paidStatus.innerHTML = 'Pix pago com sucesso!';
            });
            setTimeout(() => {
                paidStatus.classList.remove('success');
                paidStatus.innerHTML = '';
            }, 5000);
            clearInterval(interval);
            // Reseta o formulário
            sectionGerarPix.classList.remove('none');
            sectionQrCode.classList.remove('show');
            form.reset();
        }
        if (timeNow - time > 310000) {
            setTimeout(() => {
                paidStatus.classList.add('error');
                paidStatus.innerHTML = 'Tempo excedido para pagamento do pix';
            });
            setTimeout(() => {
                paidStatus.classList.remove('error');
                paidStatus.innerHTML = '';
            }, 5000); 
            clearInterval(interval);
            // Reseta o formulário
            sectionGerarPix.classList.remove('none');
            sectionQrCode.classList.remove('show');
            form.reset();
        }
    }, 5000);

    newQrCode.addEventListener('click', () => {
        sectionGerarPix.classList.remove('none');
        sectionQrCode.classList.remove('show');
        form.reset();
        qrCodeElement.innerHTML = '';
        clearInterval(interval);
    });
});

async function generatePix(value, solicitacao_pagador){
    const response = await fetch(API_URL + "/pix", {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            value: value,
            solicitacao_pagador: solicitacao_pagador || 'Pagamento'
        })
    });

    const data = await response.json();

    return data;
}

async function generateQrCode(data){
    qrCodeElement.innerHTML = '';
    let qrCode = new QRCode(qrCodeElement, {
        text: data,
        width: 250,
        height: 250,
        colorDark: "#000000",
        colorLight: "#ffffff",
        correctLevel: QRCode.CorrectLevel.H
    });

    qrCode.makeCode(data);
}

// Verifica o pix foi pago
async function checkPix(txId){
    const response = await fetch(API_URL + `/pix/${txId}/status`, {
        method: 'GET'
    });

    if (response.status == 200) {
        const data = await response.json();
        //console.log(data);
        if (data.message == 'PAGO') {
            return true;
        }
    }

    return false;
}