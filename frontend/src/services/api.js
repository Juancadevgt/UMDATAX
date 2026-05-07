import axios from "axios";

const BASE_URL = "https://umdatax-backend.onrender.com";

export const procesarArchivo = async (file, tipo, campos) => {
  const formData = new FormData();
  formData.append("file", file);
  formData.append("tipo", tipo);
  formData.append("campos", campos.join(","));

  const response = await axios.post(
    `${BASE_URL}/procesar/`,
    formData,
    { responseType: "blob" }
  );

  return response.data;
};

export const exportarReportePBI = async (url, nombre) => {
  const response = await axios.post(
    `${BASE_URL}/exportar-pbi/`,
    { url, nombre },
    { responseType: "blob" }
  );

  return response.data;
};