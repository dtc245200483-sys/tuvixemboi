"use strict";
var __createBinding = (this && this.__createBinding) || (Object.create ? (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    var desc = Object.getOwnPropertyDescriptor(m, k);
    if (!desc || ("get" in desc ? !m.__esModule : desc.writable || desc.configurable)) {
      desc = { enumerable: true, get: function() { return m[k]; } };
    }
    Object.defineProperty(o, k2, desc);
}) : (function(o, m, k, k2) {
    if (k2 === undefined) k2 = k;
    o[k2] = m[k];
}));
var __setModuleDefault = (this && this.__setModuleDefault) || (Object.create ? (function(o, v) {
    Object.defineProperty(o, "default", { enumerable: true, value: v });
}) : function(o, v) {
    o["default"] = v;
});
var __importStar = (this && this.__importStar) || function (mod) {
    if (mod && mod.__esModule) return mod;
    var result = {};
    if (mod != null) for (var k in mod) if (k !== "default" && Object.prototype.hasOwnProperty.call(mod, k)) __createBinding(result, mod, k);
    __setModuleDefault(result, mod);
    return result;
};
var __exportStar = (this && this.__exportStar) || function(m, exports) {
    for (var p in m) if (p !== "default" && !Object.prototype.hasOwnProperty.call(exports, p)) __createBinding(exports, m, p);
};
Object.defineProperty(exports, "__esModule", { value: true });
exports.isBadStar = exports.BAD_STAR_NAMES = exports.MAJOR_STAR_NAMES = exports.SOUL_MASTER_MAP = exports.getStarHanh = exports.STAR_ELEMENT_MAP = exports.getVietnameseMutagenTable = exports.calculateYearlyStars = exports.calculateSoulMasterStar = exports.calculateKuiYue = exports.calculateHuoLing = exports.calculateTuanTriet = exports.calculateTuanBranches = exports.calculateTrietBranches = exports.getCanChiFromYear = exports.astrolabeByLunarDate = exports.astrolabeBySolarDate = exports.applyVietnamAstrologyRules = exports.vietnamAstrologyAdapter = exports.vietnamese = exports.astro = exports.util = exports.star = exports.data = void 0;
exports.data = __importStar(require("./data"));
exports.star = __importStar(require("./star"));
exports.util = __importStar(require("./utils"));
exports.astro = __importStar(require("./astro"));
__exportStar(require("./overlayEngine"), exports);
__exportStar(require("./components/PalaceOverlay"), exports);
__exportStar(require("./components/OverlayToolbar"), exports);
exports.vietnamese = __importStar(require("./vietnamese"));
__exportStar(require("./vietnamese"), exports);
var vietnamAstrologyAdapter_1 = require("./vietnamAstrologyAdapter");
Object.defineProperty(exports, "vietnamAstrologyAdapter", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.vietnamAstrologyAdapter; } });
Object.defineProperty(exports, "applyVietnamAstrologyRules", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.applyVietnamAstrologyRules; } });
Object.defineProperty(exports, "astrolabeBySolarDate", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.astrolabeBySolarDate; } });
Object.defineProperty(exports, "astrolabeByLunarDate", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.astrolabeByLunarDate; } });
Object.defineProperty(exports, "getCanChiFromYear", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getCanChiFromYear; } });
Object.defineProperty(exports, "calculateTrietBranches", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTrietBranches; } });
Object.defineProperty(exports, "calculateTuanBranches", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTuanBranches; } });
Object.defineProperty(exports, "calculateTuanTriet", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateTuanTriet; } });
Object.defineProperty(exports, "calculateHuoLing", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateHuoLing; } });
Object.defineProperty(exports, "calculateKuiYue", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateKuiYue; } });
Object.defineProperty(exports, "calculateSoulMasterStar", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateSoulMasterStar; } });
Object.defineProperty(exports, "calculateYearlyStars", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.calculateYearlyStars; } });
Object.defineProperty(exports, "getVietnameseMutagenTable", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getVietnameseMutagenTable; } });
Object.defineProperty(exports, "STAR_ELEMENT_MAP", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.STAR_ELEMENT_MAP; } });
Object.defineProperty(exports, "getStarHanh", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.getStarHanh; } });
Object.defineProperty(exports, "SOUL_MASTER_MAP", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.SOUL_MASTER_MAP; } });
Object.defineProperty(exports, "MAJOR_STAR_NAMES", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.MAJOR_STAR_NAMES; } });
Object.defineProperty(exports, "BAD_STAR_NAMES", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.BAD_STAR_NAMES; } });
Object.defineProperty(exports, "isBadStar", { enumerable: true, get: function () { return vietnamAstrologyAdapter_1.isBadStar; } });
