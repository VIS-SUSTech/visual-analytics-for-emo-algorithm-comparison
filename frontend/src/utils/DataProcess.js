import * as d3 from "d3";
import _ from "lodash";

export const getScalers = (
  domainX = [0, 0],
  domainY = [0, 0],
  margin = 0,
  viewSizeW = 0,
  viewSizeH
) => {
  if (_.isUndefined(viewSizeH)) {
    viewSizeH = viewSizeW;
  }

  const scaleX = d3.scaleLinear().domain(domainX).nice().range([0, 100]);
  const scaleY = d3.scaleLinear().domain(domainY).nice().range([0, 100]);
  const axisScaleX = d3
    .scaleLinear()
    .domain(scaleX.range())
    .range([margin, margin + viewSizeW]);
  const axisScaleY = d3
    .scaleLinear()
    .domain(scaleY.range())
    .range([margin + viewSizeH, margin]);
  const scaler = ([x, y]) => [scaleX(x), scaleY(y)];

  return [scaler, axisScaleX, axisScaleY];
};

export const getDirectScalers = (
  domainX = [0, 0],
  domainY = [0, 0],
  margin = 0,
  viewSizeW = 0,
  viewSizeH
) => {
  if (_.isUndefined(viewSizeH)) {
    viewSizeH = viewSizeW;
  }

  const scaleX = d3
    .scaleLinear()
    .domain(domainX)
    .range([margin, margin + viewSizeW]);
  const scaleY = d3
    .scaleLinear()
    .domain(domainY)
    .range([margin + viewSizeH, margin]);

  return [scaleX, scaleY];
};

export const getLimitedNumber = (value) => {
  const initStr = _.toString(value);

  if (_.size(initStr) <= 5) {
    return value;
  }
  return _.toNumber(value).toExponential(1);
};

export const getExponentialNumber = (value, digits) =>
  _.toNumber(value).toExponential(digits);

export const getNaiveSelectItems = (options) =>
  _.map(options, (opt) => ({ label: opt, value: opt }));

export const getIndexSeries = (frames) =>
  _.fromPairs(_.map(frames, (f, index) => [f, index + 1]));
