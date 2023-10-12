import _ from "lodash";

const baseURL = `http://${window.location.hostname}:5100`;
const encode = encodeURIComponent;

export const getInfo = (name, callback, errorHandler) =>
  fetch(`${baseURL}/info/${encode(name)}`)
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });

export const getData = (name, callback, errorHandler) =>
  fetch(`${baseURL}/data/${encode(name)}`)
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });

export const getObjVector = (name, algorithm, frame, callback, errorHandler) =>
  fetch(
    `${baseURL}/obj_vec/${encode(name)}/${encode(algorithm)}/${encode(frame)}`
  )
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });

export const getAttachment = (name, algorithm, callback, errorHandler) =>
  fetch(`${baseURL}/attachment/${encode(name)}/${encode(algorithm)}`)
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });

export const getGraph = (name, payload, callback, errorHandler) =>
  fetch(`${baseURL}/graph/${encode(name)}`, {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });

export const getSampling = (payload, callback, errorHandler) =>
  fetch(`${baseURL}/sampling`, {
    method: "POST",
    body: JSON.stringify(payload),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then((response) => response.json())
    .then((data) => {
      if (_.isFunction(callback)) {
        callback(data);
      }
    })
    .catch((error) => {
      if (_.isFunction(errorHandler)) {
        errorHandler(error);
      } else {
        console.error(error);
      }
    });
