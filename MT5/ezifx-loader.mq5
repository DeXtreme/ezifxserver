//+------------------------------------------------------------------+
//|                                                 ezifx-loader.mq5 |
//|                        Copyright 2020, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2020, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   //Open charts and attach EAs
   long chartid=ChartOpen("EURUSD",PERIOD_H1);
   ChartApplyTemplate(chartid,"eurusd.tpl");
   //chartid=ChartOpen("USDJPY",PERIOD_H4);
   //ChartApplyTemplate(chartid,"usdjpy.tpl");
   //chartid=ChartOpen("GBPUSD",PERIOD_H12);
   //ChartApplyTemplate(chartid,"gbpusd.tpl");
      
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
//---
   
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
//---
   
  }
//+------------------------------------------------------------------+
