//+------------------------------------------------------------------+
//|                                        ezifx-gen-test-eurusd.mq5 |
//|                        Copyright 2020, MetaQuotes Software Corp. |
//|                                             https://www.mql5.com |
//+------------------------------------------------------------------+
#property copyright "Copyright 2020, MetaQuotes Software Corp."
#property link      "https://www.mql5.com"
#property version   "1.00"
//--- input parameters
input string   token="8d15f5ee4db8cab6a9628423b88f31bca9f5817b";
input int      D1Fast=1;
input int      D1Slow=7;
input int      H4Fast=1;
input int      H4Slow=6;
input int      H1Fast=4;
input int      H1Slow=24;
input int      M30Fast=1;
input int      M30Slow=2;
input int      M15Fast=1;
input int      M15Slow=4;

double previous_tenkan_D1=0;
double previous_tenkan_H4=0;
double previous_tenkan_H1=0;
double previous_tenkan_M30=0;
double previous_tenkan_M15=0;
string min_lot;
//+------------------------------------------------------------------+
//| Expert initialization function                                   |
//+------------------------------------------------------------------+
int OnInit()
  {
   min_lot=DoubleToString(SymbolInfoDouble(Symbol(),SYMBOL_VOLUME_MIN));
   for(int i=0;i<5;i++)
        {
         int FastPeriod=0;
         int SlowPeriod=0;
         ENUM_TIMEFRAMES IndicatorPeriod=0;
         switch(i)
           {
            case 0:
              FastPeriod=D1Fast;
              SlowPeriod=D1Slow;
              IndicatorPeriod=PERIOD_D1;
              break;
            case 1:
              FastPeriod=H4Fast;
              SlowPeriod=H4Slow;
              IndicatorPeriod=PERIOD_H4;
              break;
            case 2:
              FastPeriod=H1Fast;
              SlowPeriod=H1Slow;
              IndicatorPeriod=PERIOD_H1;
              break;
            case 3:
              FastPeriod=M30Fast;
              SlowPeriod=M30Slow;
              IndicatorPeriod=PERIOD_M30;
              break;
            case 4:
              FastPeriod=M15Fast;
              SlowPeriod=M15Slow;
              IndicatorPeriod=PERIOD_M15;
              break;
            default:
              break;
           }
           
            double TenkansanArray[];
            ArraySetAsSeries(TenkansanArray,true);
            
            int ichimoku=iIchimoku(NULL,IndicatorPeriod,FastPeriod,SlowPeriod,30);
            CopyBuffer(ichimoku,0,2,1,TenkansanArray);
            
            switch(i)
           {
            case 0:
              previous_tenkan_D1=TenkansanArray[0];
              break;
            case 1:
              previous_tenkan_H4=TenkansanArray[0];
              break;
            case 2:
              previous_tenkan_H1=TenkansanArray[0];
              break;
            case 3:
              previous_tenkan_M30=TenkansanArray[0];
              break;
            case 4:
              previous_tenkan_M15=TenkansanArray[0];
              break;
            default:
              break;
           }           
 
         }
   return(INIT_SUCCEEDED);
  }
//+------------------------------------------------------------------+
//| Expert deinitialization function                                 |
//+------------------------------------------------------------------+
void OnDeinit(const int reason)
  {
     
  }
//+------------------------------------------------------------------+
//| Expert tick function                                             |
//+------------------------------------------------------------------+
void OnTick()
  {
       for(int i=0;i<5;i++) //do for each period
        {
         int FastPeriod=0;
         int SlowPeriod=0;
         ENUM_TIMEFRAMES IndicatorPeriod=0;
         double previous_tenkan=0;
         
         switch(i)
           {
            case 0:
              FastPeriod=D1Fast;
              SlowPeriod=D1Slow;
              IndicatorPeriod=PERIOD_D1;
              previous_tenkan=previous_tenkan_D1;
              break;
            case 1:
              FastPeriod=H4Fast;
              SlowPeriod=H4Slow;
              IndicatorPeriod=PERIOD_H4;
              previous_tenkan=previous_tenkan_H4;
              break;
            case 2:
              FastPeriod=H1Fast;
              SlowPeriod=H1Slow;
              IndicatorPeriod=PERIOD_H1;
              previous_tenkan=previous_tenkan_H1;
              break;
            case 3:
              FastPeriod=M30Fast;
              SlowPeriod=M30Slow;
              IndicatorPeriod=PERIOD_M30;
              previous_tenkan=previous_tenkan_M30;
              break;
            case 4:
              FastPeriod=M15Fast;
              SlowPeriod=M15Slow;
              IndicatorPeriod=PERIOD_M15;
              previous_tenkan=previous_tenkan_M15;
              break;
            default:
              break;
           }
           
           
            double TenkansanArray[];
            double KijunsanArray[];
            ArraySetAsSeries(TenkansanArray,true);
            ArraySetAsSeries(KijunsanArray,true);
            
            int ichimoku=iIchimoku(NULL,IndicatorPeriod,FastPeriod,SlowPeriod,30);
            CopyBuffer(ichimoku,0,1,1,TenkansanArray);
            CopyBuffer(ichimoku,1,1,1,KijunsanArray);
                               
            double current_tenkan=TenkansanArray[0];
            double kijun=KijunsanArray[0];
            
            double HAOpenArray[];
            double HACloseArray[];
            ArraySetAsSeries(HAOpenArray,true);
            ArraySetAsSeries(HACloseArray,true);
            
            int HA=iCustom(NULL,IndicatorPeriod,"heiken_ashi");
            
            CopyBuffer(HA,0,1,1,HAOpenArray);
            CopyBuffer(HA,3,1,1,HACloseArray);
           
            double HAOpen=HAOpenArray[0];
            double HAClose=HACloseArray[0];
            
            
            if(current_tenkan>kijun && previous_tenkan<=kijun){
               if(HAClose>HAOpen && HAClose>=kijun){
                  previous_tenkan=current_tenkan;
                  Print("Buying",IntegerToString(i));
                  MqlTradeRequest request={0};
                  MqlTradeResult  result={0};
                  
                  request.action   =TRADE_ACTION_DEAL;                     // type of trade operation
                  request.symbol   =Symbol();                              // symbol
                  request.volume   =0.01;                                   // volume of 0.1 lot
                  request.type     =ORDER_TYPE_BUY;                        // order type
                  request.price    =SymbolInfoDouble(Symbol(),SYMBOL_ASK); // price for opening
                  request.deviation=5;                                     // allowed deviation from the price
                  request.type_filling=ORDER_FILLING_FOK;
                  OrderSend(request,result);
                  
                  SendSignal("BY",IndicatorPeriod,SlowPeriod);
               }else{
                  previous_tenkan=current_tenkan;
               }
            }else if(current_tenkan<kijun && previous_tenkan>=kijun){
               if(HAClose<HAOpen && HAClose<=kijun){
                  previous_tenkan=current_tenkan;
                  Print("Selling",IntegerToString(i));
                  MqlTradeRequest request={0};
                  MqlTradeResult  result={0};
                  
                  request.action   =TRADE_ACTION_DEAL;                     // type of trade operation
                  request.symbol   =Symbol();                              // symbol
                  request.volume   =0.01;                                   // volume of 0.1 lot
                  request.type     =ORDER_TYPE_SELL;                        // order type
                  request.price    =SymbolInfoDouble(Symbol(),SYMBOL_BID); // price for opening
                  request.deviation=5;                                     // allowed deviation from the price
                  request.type_filling=ORDER_FILLING_FOK;
                  OrderSend(request,result);
                  SendSignal("SL",IndicatorPeriod,SlowPeriod);
               }else{
                  previous_tenkan=current_tenkan;
               }
            }else{
               previous_tenkan=current_tenkan;
            } 
            
            switch(i)
           {
            case 0:
              previous_tenkan_D1=previous_tenkan;
              break;
            case 1:
              previous_tenkan_H4=previous_tenkan;
              break;
            case 2:
              previous_tenkan_H1=previous_tenkan;
              break;
            case 3:
              previous_tenkan_M30=previous_tenkan;
              break;
            case 4:
              previous_tenkan_M15=previous_tenkan;
              break;
            default:
              break;
           }
            
        }
   
  }
//+------------------------------------------------------------------+
void SendSignal(string action,ENUM_TIMEFRAMES IndicatorPeriod,int SlowPeriod){
   double ATRArray[];
   int ATRin=iATR(NULL,IndicatorPeriod,SlowPeriod);
   ArraySetAsSeries(ATRArray,true);
   CopyBuffer(ATRin,0,0,1,ATRArray);
   double atr=ATRArray[0];
   
   if(Digits()==5 || Digits()==4)
     {
      atr=atr*10000;
     }
     
   if(Digits()==3 || Digits()==2)
     {
      atr=atr*100;
     }
   string body;
   StringConcatenate(body,"{","\"pair\":\"",Symbol(),"\",\"action\":\"",action,"\",\"timeframe\":\"",getTimeframe(IndicatorPeriod),"\",\"atr\":",DoubleToString(atr),",",
   "\"min_lot\":",min_lot,",","\"bars\":[");
   double CloseArray[];
   ArraySetAsSeries(CloseArray,true);
   CopyClose(Symbol(),IndicatorPeriod,0,15,CloseArray);
   for(int i=10;i>0;i--)
     {
         StringAdd(body,DoubleToString(CloseArray[i]));
         StringAdd(body,",");
     }
   StringAdd(body,DoubleToString(CloseArray[0]));
   StringAdd(body,"]}");
   Print(body);
   
   string headers;
   StringConcatenate(headers,"Content-Type:application/json\r\nAUTHORIZATION: Token ",token);
   
   char post[],response[];
   string response_headers,strResponse;
   StringToCharArray(body,post,0,StringLen(body));
   int result=WebRequest("POST","http://127.0.0.1/v1/signals/",headers,2000,post,response,response_headers);
   
   if(result==-1){
      Print("Error ",GetLastError());
   }
   
   for(int i=0;i<ArraySize(response);i++)
      {
         if( (response[i] == 10) || (response[i] == 13)) {
            continue;
         } else {
            strResponse += CharToString(response[i]);
         }
      }
   Print(strResponse);       
}

string getTimeframe(ENUM_TIMEFRAMES period){
   switch(period)
     {
      case PERIOD_M15:
        return "M15";
      case PERIOD_M30:
        return "M30";
      case PERIOD_H1:
        return "H1";
      case PERIOD_H4:
        return "H4";
      case PERIOD_D1:
        return "D1";
      default:
        return "H1";
     }
}