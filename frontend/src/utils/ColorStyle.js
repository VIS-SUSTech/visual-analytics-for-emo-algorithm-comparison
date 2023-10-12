import _ from "lodash";

export const colors = {
  // name: [light, normal, dark]
  green: ["#72CA9B", "#238551", "#165A36"],
  blue: ["#8ABBFF", "#2D72D2", "#184A90"],
  orange: ["#FBB360", "#C87619", "#77450D"],
  red: ["#FA999C", "#CD4246", "#8E292C"],
  indigo: ["#D6CCFF", "#9784D2", "#5642A6"],
  turquoise: ["#97F3EB", "#58B8AE", "#008075"],
  vermilion: ["#FFB7A5", "#D17257", "#9E2B0E"],
  rose: ["#FFB3D0", "#D56F90", "#A82255"],
  gold: ["#FFE4A0", "#D4AD5A", "#A67908"],
  violet: ["#E1BAE1", "#9D6D9C", "#5C255C"],
  forest: ["#B1ECB5", "#6AAE6A", "#1D7324"],
  cerulean: ["#B3CFFF", "#6F8ACB", "#1F4B99"],
  lime: ["#E8F9B6", "#ADC16D", "#728C23"],
  sepial: ["#E4CBB2", "#A38364", "#63411E"],
  // Inactived Color
  none: ["#d9d9d9", "#8c8c8c", "#434343"],
};

export const colorKeys = _.without(_.keys(colors), "none");

export const initColorMap = () => _.fromPairs(_.map(colorKeys, (c) => [c, 0]));
