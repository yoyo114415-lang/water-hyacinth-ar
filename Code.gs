/**
 * ====================================================================
 * 水生植物 3D Web-AR 互動學習平台 (GAS 專案端)
 * ====================================================================
 * 實作任務：漂浮性水生植物 ── 布袋蓮 (Water Hyacinth)
 * 小組資訊：第 3 組 ｜ 綠境探索隊 (E-Learning Team 03)
 * 核心功能：透過手機鏡頭掃描 AR Code，即時於鏡頭實景畫面浮現 3D 模型
 * ====================================================================
 */

function doGet(e) {
  var template = HtmlService.createTemplateFromFile('index');
  var output = template.evaluate()
    .setTitle('水生植物 3D Web-AR 互動學習平台 ｜ 第 3 組')
    .addMetaTag('viewport', 'width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no')
    .setXFrameOptionsMode(HtmlService.XFrameOptionsMode.ALLOWALL);
  return output;
}
