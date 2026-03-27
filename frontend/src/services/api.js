import axios from "axios";

export const procesarArchivo = async (file, tipo, campos) => {
  const formData = new FormData();

  formData.append("file", file);
  formData.append("tipo", tipo);
  formData.append("campos", campos.join(","));

  const response = await axios.post(
    "http://127.0.0.1:8000/procesar/",
    formData,
    {
      responseType: "blob" // 🔥 CLAVE
    }
  );

  return response.data;
};