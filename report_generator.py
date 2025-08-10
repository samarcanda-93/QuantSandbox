import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import os
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
import finance_utils

class StrategyReportGenerator:
    """Generate PDF reports for strategy analysis results."""
    
    def __init__(self, ticker):
        self.ticker = ticker
        
    def generate_basic_report(self, results, filename=None):
        """Generate PDF report for basic strategy comparison."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"strategy_report_{self.ticker}_{timestamp}.pdf"
        
        with PdfPages(filename) as pdf:
            # Page 1: Summary
            self._create_summary_page(pdf, results)
            
            # Page 2: Portfolio Performance Chart
            self._create_portfolio_chart_page(pdf, results)
            
            # Page 3: Risk Metrics
            self._create_risk_metrics_page(pdf, results)
        
        return filename
    
    def generate_full_report(self, mr_results, mom_results, mr_best_params, mom_best_params, filename=None):
        """Generate comprehensive PDF report for full parameter exploration."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"full_analysis_report_{self.ticker}_{timestamp}.pdf"
        
        with PdfPages(filename) as pdf:
            # Page 1: Executive Summary
            self._create_executive_summary_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
            
            # Page 2: Strategy Performance Overview
            self._create_strategy_overview_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
            
            # Page 3: Parameter Analysis Charts
            self._create_parameter_charts_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
            
            # Page 4: AI Analysis & Key Insights  
            self._create_insights_page(pdf, mr_results, mom_results, mr_best_params, mom_best_params)
            
            # Page 5: Glossary
            self._create_glossary_page(pdf)
        
        return filename
    
    def _create_summary_page(self, pdf, results):
        """Create summary page for basic report."""
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 format
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Strategy Analysis Report - {self.ticker}', fontsize=20, fontweight='bold')
        
        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(0.1, 0.9, f'Report Generated: {report_date}', fontsize=12, transform=ax.transAxes)
        ax.text(0.1, 0.85, f'Ticker: {self.ticker}', fontsize=12, fontweight='bold', transform=ax.transAxes)
        
        # Strategy results
        y_pos = 0.75
        ax.text(0.1, y_pos, 'STRATEGY PERFORMANCE SUMMARY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        
        y_pos -= 0.08
        for strategy_name, data in results.items():
            strategy_title = strategy_name.replace('_', ' ').title()
            ax.text(0.1, y_pos, f'{strategy_title}:', fontsize=14, fontweight='bold', transform=ax.transAxes)
            
            y_pos -= 0.05
            sharpe = data['sharpe']
            if sharpe is not None:
                ax.text(0.15, y_pos, f'Sharpe Ratio: {sharpe:.4f}', fontsize=12, transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, 'Sharpe Ratio: Unable to calculate', fontsize=12, transform=ax.transAxes)
            
            y_pos -= 0.04
            drawdown = data['drawdown']['max_drawdown']
            if drawdown is not None:
                ax.text(0.15, y_pos, f'Max Drawdown: {drawdown:.2%}', fontsize=12, transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, 'Max Drawdown: N/A', fontsize=12, transform=ax.transAxes)
            
            # Parameters
            y_pos -= 0.04
            params = data['params']
            param_text = ', '.join([f'{k.title()}: {v}' for k, v in params.items()])
            ax.text(0.15, y_pos, f'Parameters: {param_text}', fontsize=12, transform=ax.transAxes)
            
            y_pos -= 0.08
        
        # Winner determination
        sharpes = [data['sharpe'] for data in results.values() if data['sharpe'] is not None]
        if sharpes:
            best_strategy = max(results.keys(), key=lambda k: results[k]['sharpe'] if results[k]['sharpe'] else -np.inf)
            ax.text(0.1, y_pos, f'BEST PERFORMING STRATEGY: {best_strategy.replace("_", " ").title()}', 
                   fontsize=14, fontweight='bold', color='green', transform=ax.transAxes)

            # Today's suggestion from the best-performing strategy
            try:
                y_pos -= 0.06
                rec = finance_utils.latest_trade_recommendation(results[best_strategy]['data'], ticker=self.ticker)
                if rec and rec.get('as_of_date') is not None:
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                    ax.text(0.1, y_pos, f"TODAY'S SUGGESTION: {rec['action']} ({rec['state']}) as of {date_str}{price_str}",
                            fontsize=12, fontweight='bold', color='black', transform=ax.transAxes)
                    y_pos -= 0.035
                    ax.text(0.1, y_pos, "Note: This is not financial advice.", fontsize=10, color='dimgray', transform=ax.transAxes)
            except Exception:
                pass
        
        # Add disclaimer as footnote
        disclaimer = ("DISCLAIMER: This report is for educational purposes only and does not constitute financial advice. "
                     "Past performance does not guarantee future results. Trading involves risk and can result in losses. "
                     "Consult a qualified financial advisor before making investment decisions.")
        ax.text(0.05, 0.02, disclaimer, transform=ax.transAxes, fontsize=7,
                verticalalignment='bottom', style='italic', color='gray', wrap=True)
        
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_portfolio_chart_page(self, pdf, results):
        """Create portfolio performance chart page."""
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 format
        
        for strategy_name, data in results.items():
            portfolio_data = data['data']
            sharpe = data.get('sharpe')
            drawdown = None
            if isinstance(data.get('drawdown'), dict):
                drawdown = data['drawdown'].get('max_drawdown')

            label = f"{strategy_name.replace('_', ' ').title()}"
            metrics = []
            if sharpe is not None:
                metrics.append(f"Sharpe: {sharpe:.3f}")
            if drawdown is not None:
                metrics.append(f"DD: {drawdown:.2%}")
            if metrics:
                label += " (" + ", ".join(metrics) + ")"

            ax.plot(portfolio_data.index, portfolio_data['PortfolioValue'], label=label, linewidth=2)
        
        ax.set_title(f'Portfolio Value Evolution - {self.ticker}', fontsize=16, fontweight='bold')
        ax.set_ylabel('Portfolio Value', fontsize=12)
        ax.set_xlabel('Date', fontsize=12)
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3)
        
        # Rotate x-axis labels for better readability
        plt.xticks(rotation=45)
        
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_risk_metrics_page(self, pdf, results):
        """Create risk metrics comparison page."""
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(8.27, 11.69))  # A4 format
        
        # Sharpe Ratio Comparison
        strategies = list(results.keys())
        sharpe_ratios = [results[s]['sharpe'] if results[s]['sharpe'] else 0 for s in strategies]
        strategy_labels = [s.replace('_', ' ').title() for s in strategies]
        
        bars1 = ax1.bar(strategy_labels, sharpe_ratios, color=['blue', 'red'])
        ax1.set_title('Sharpe Ratio Comparison', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Sharpe Ratio')
        ax1.grid(True, alpha=0.3, axis='y')
        
        # Add value labels on bars
        for bar, value in zip(bars1, sharpe_ratios):
            if value != 0:
                ax1.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01, 
                        f'{value:.3f}', ha='center', va='bottom')
        
        # Max Drawdown Comparison
        drawdowns = [results[s]['drawdown']['max_drawdown'] if results[s]['drawdown']['max_drawdown'] else 0 for s in strategies]
        bars2 = ax2.bar(strategy_labels, drawdowns, color=['blue', 'red'])
        ax2.set_title('Maximum Drawdown Comparison', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Max Drawdown')
        ax2.grid(True, alpha=0.3, axis='y')
        
        # Format y-axis as percentage
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
        
        # Add value labels on bars
        for bar, value in zip(bars2, drawdowns):
            if value != 0:
                ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.005, 
                        f'{value:.2%}', ha='center', va='bottom')
        
        plt.tight_layout()
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_executive_summary_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create executive summary for full analysis report."""
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 format
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Comprehensive Strategy Analysis - {self.ticker}', fontsize=18, fontweight='bold')
        
        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        ax.text(0.1, 0.9, f'Report Generated: {report_date}', fontsize=12, transform=ax.transAxes)
        
        y_pos = 0.8
        
        # Mean Reversion Summary
        ax.text(0.1, y_pos, 'MEAN REVERSION STRATEGY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mr_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            ax.text(0.15, y_pos, f'Best Parameters: Window={mr_best_params[0]}, Threshold={mr_best_params[1]:.3f}', 
                   fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            ax.text(0.15, y_pos, f'Sharpe Ratio: {best_mr["Sharpe_Ratio"]:.4f}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            if best_mr['Max_Drawdown']:
                ax.text(0.15, y_pos, f'Max Drawdown: {best_mr["Max_Drawdown"]:.2%}', fontsize=12, transform=ax.transAxes)
        
        y_pos -= 0.08
        
        # Momentum Summary
        ax.text(0.1, y_pos, 'MOMENTUM STRATEGY', fontsize=16, fontweight='bold', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mom_best_params:
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            ax.text(0.15, y_pos, f'Best Parameter: Window={mom_best_params}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            ax.text(0.15, y_pos, f'Sharpe Ratio: {best_mom["Sharpe_Ratio"]:.4f}', fontsize=12, transform=ax.transAxes)
            y_pos -= 0.04
            if best_mom['Max_Drawdown']:
                ax.text(0.15, y_pos, f'Max Drawdown: {best_mom["Max_Drawdown"]:.2%}', fontsize=12, transform=ax.transAxes)
        
        # Overall recommendation
        y_pos -= 0.1
        ax.text(0.1, y_pos, 'RECOMMENDATION', fontsize=16, fontweight='bold', color='green', transform=ax.transAxes)
        y_pos -= 0.05
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            if best_mr['Sharpe_Ratio'] > best_mom['Sharpe_Ratio']:
                ax.text(0.15, y_pos, f'Mean Reversion strategy is recommended', fontsize=12, fontweight='bold', transform=ax.transAxes)
            else:
                ax.text(0.15, y_pos, f'Momentum strategy is recommended', fontsize=12, fontweight='bold', transform=ax.transAxes)

            # Today's suggestion from the higher-Sharpe best strategy
            try:
                y_pos -= 0.06
                preferred = best_mr if best_mr['Sharpe_Ratio'] >= best_mom['Sharpe_Ratio'] else best_mom
                rec = finance_utils.latest_trade_recommendation(preferred['Data'], ticker=self.ticker)
                if rec and rec.get('as_of_date') is not None:
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') is not None else ""
                    ax.text(0.15, y_pos, f"TODAY'S SUGGESTION: {rec['action']} ({rec['state']}) as of {date_str}{price_str}",
                            fontsize=12, fontweight='bold', color='black', transform=ax.transAxes)
                    y_pos -= 0.035
                    ax.text(0.15, y_pos, "Note: This is not financial advice.", fontsize=10, color='dimgray', transform=ax.transAxes)
            except Exception:
                pass
        
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_strategy_overview_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create strategy performance overview page with single column layout."""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 format
        fig.suptitle(f'Strategy Performance Overview - {self.ticker}', fontsize=14, fontweight='bold', y=0.95)
        
        # Create 4 subplots in single column
        ax1 = plt.subplot(4, 1, 1)
        ax2 = plt.subplot(4, 1, 2)
        ax3 = plt.subplot(4, 1, 3)
        ax4 = plt.subplot(4, 1, 4)
        
        if mr_best_params and mom_best_params:
            # Get best results
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            # Portfolio Performance Comparison
            mr_data = best_mr['Data']
            mom_data = best_mom['Data']
            
            ax1.plot(mr_data.index, mr_data['PortfolioValue'], 
                    label=f'Mean Reversion', linewidth=2, color='blue')
            ax1.plot(mom_data.index, mom_data['PortfolioValue'], 
                    label=f'Momentum', linewidth=2, color='red')
            ax1.set_title('Portfolio Value Evolution', fontsize=12, pad=10)
            ax1.set_ylabel('Portfolio Value ($)', fontsize=10)
            ax1.legend(loc='upper left', fontsize=9)
            ax1.grid(True, alpha=0.3)
            
            # No caption - information is in legend
            
            # Price with Best Strategy Signals
            if best_mr['Sharpe_Ratio'] >= best_mom['Sharpe_Ratio']:
                best_data = mr_data
                strategy_name = 'Mean Reversion'
            else:
                best_data = mom_data
                strategy_name = 'Momentum'
            
            ax2.plot(best_data.index, best_data[f'Close_{self.ticker}'], 
                    label=f'{self.ticker}', color='black', linewidth=1.5)
            
            buy_signals = best_data[best_data['Position'] == 1]
            sell_signals = best_data[best_data['Position'] == -1]
            
            if not buy_signals.empty:
                ax2.scatter(buy_signals.index, buy_signals[f'Close_{self.ticker}'], 
                           marker='^', color='green', s=25, label='Buy', alpha=0.8, zorder=5)
            if not sell_signals.empty:
                ax2.scatter(sell_signals.index, sell_signals[f'Close_{self.ticker}'], 
                           marker='v', color='red', s=25, label='Sell', alpha=0.8, zorder=5)
            
            ax2.set_title(f'Trading Signals: {strategy_name}', fontsize=12, pad=10)
            ax2.set_ylabel('Price ($)', fontsize=10)
            ax2.legend(loc='upper left', fontsize=9)
            ax2.grid(True, alpha=0.3)
            
            # No caption - information is in legend
            
            # Performance Metrics Bar Chart
            strategies = ['Mean Rev.', 'Momentum']
            sharpe_values = [best_mr['Sharpe_Ratio'], best_mom['Sharpe_Ratio']]
            colors = ['blue', 'red']
            
            bars = ax3.bar(strategies, sharpe_values, color=colors, alpha=0.7, width=0.6)
            ax3.set_title('Sharpe Ratio Comparison', fontsize=12, pad=10)
            ax3.set_ylabel('Sharpe Ratio', fontsize=10)
            ax3.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars, sharpe_values):
                height = bar.get_height()
                ax3.text(bar.get_x() + bar.get_width()/2, height + 0.02, 
                        f'{value:.3f}', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            # No caption needed
            
            # Risk Metrics
            drawdown_values = [best_mr['Max_Drawdown'], best_mom['Max_Drawdown']]
            bars2 = ax4.bar(strategies, drawdown_values, color=colors, alpha=0.7, width=0.6)
            ax4.set_title('Maximum Drawdown', fontsize=12, pad=10)
            ax4.set_ylabel('Max Drawdown', fontsize=10)
            ax4.yaxis.set_major_formatter(plt.FuncFormatter(lambda x, p: f'{x:.1%}'))
            ax4.grid(True, alpha=0.3, axis='y')
            
            # Add value labels on bars
            for bar, value in zip(bars2, drawdown_values):
                if value is not None:
                    height = bar.get_height()
                    ax4.text(bar.get_x() + bar.get_width()/2, height + 0.005, 
                            f'{value:.1%}', ha='center', va='bottom', fontweight='bold', fontsize=9)
            
            # No caption needed
        
        # Single column layout with proper spacing
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.05, hspace=0.4)
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_parameter_charts_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create parameter analysis charts page with single column layout."""
        fig = plt.figure(figsize=(8.27, 11.69))  # A4 format
        fig.suptitle('Parameter Sensitivity Analysis', fontsize=14, fontweight='bold', y=0.95)
        
        # Create 3 subplots in single column (2 charts + 1 summary)
        ax1 = plt.subplot(3, 1, 1)
        ax2 = plt.subplot(3, 1, 2)
        ax3 = plt.subplot(3, 1, 3)
        ax3.axis('off')  # For text summary
        
        # Mean Reversion Parameter Heatmap
        if mr_results:
            mr_df = pd.DataFrame([
                {'Window': r['Window'], 'Threshold': r['Threshold'], 'Sharpe_Ratio': r['Sharpe_Ratio']} 
                for r in mr_results
            ])
            
            sharpe_pivot = mr_df.pivot(index='Window', columns='Threshold', values='Sharpe_Ratio')
            im1 = ax1.imshow(sharpe_pivot.values, cmap='RdYlGn', aspect='auto')
            ax1.set_title('Mean Reversion: Parameter Heatmap', fontsize=11, pad=8)
            ax1.set_xticks(range(len(sharpe_pivot.columns)))
            ax1.set_xticklabels([f'{x:.1%}' for x in sharpe_pivot.columns], fontsize=8)
            ax1.set_yticks(range(len(sharpe_pivot.index)))
            ax1.set_yticklabels(sharpe_pivot.index, fontsize=8)
            ax1.set_xlabel('Threshold', fontsize=9)
            ax1.set_ylabel('Window', fontsize=9)
            plt.colorbar(im1, ax=ax1, fraction=0.046, pad=0.04)
        
        # Momentum Window Performance
        if mom_results:
            mom_df = pd.DataFrame([
                {'Window': r['Window'], 'Sharpe_Ratio': r['Sharpe_Ratio']} 
                for r in mom_results
            ])
            
            bars = ax2.bar(mom_df['Window'], mom_df['Sharpe_Ratio'], color='steelblue', alpha=0.7, width=6)
            ax2.set_title('Momentum: Window Optimization', fontsize=11, pad=8)
            ax2.set_xlabel('Window Size (days)', fontsize=9)
            ax2.set_ylabel('Sharpe Ratio', fontsize=9)
            ax2.grid(True, alpha=0.3, axis='y')
            
            # Highlight best parameter
            if mom_best_params:
                best_idx = mom_df[mom_df['Window'] == mom_best_params].index[0]
                bars[best_idx].set_color('green')
                bars[best_idx].set_alpha(0.9)
        
        # Summary text without boxes
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            summary_text = f"OPTIMAL PARAMETERS:\n\n"
            summary_text += f"Mean Reversion: Window={mr_best_params[0]}d, Threshold={mr_best_params[1]:.1%}, Sharpe={best_mr['Sharpe_Ratio']:.3f}\n"
            summary_text += f"Momentum: Window={mom_best_params}d, Sharpe={best_mom['Sharpe_Ratio']:.3f}\n\n"
            winner = "Momentum" if best_mom['Sharpe_Ratio'] > best_mr['Sharpe_Ratio'] else "Mean Reversion"
            summary_text += f"RECOMMENDED: {winner} Strategy"
            
            ax3.text(0.1, 0.8, summary_text, transform=ax3.transAxes, fontsize=10, 
                    verticalalignment='top', fontfamily='monospace')
        
        # Single column spacing
        plt.subplots_adjust(left=0.1, right=0.95, top=0.9, bottom=0.05, hspace=0.4)
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_insights_page(self, pdf, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create AI insights page (A4 format)."""
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 format
        ax.axis('off')
        
        # Title
        fig.suptitle(f'Market Behavior Analysis - {self.ticker}', fontsize=14, fontweight='bold', y=0.92)
        
        insights_text = ""
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            # Determine winning strategy
            winning_strategy = "Mean Reversion" if best_mr['Sharpe_Ratio'] > best_mom['Sharpe_Ratio'] else "Momentum"
            
            # Strategy comparison
            insights_text += f"STRATEGY PERFORMANCE COMPARISON\n\n"
            insights_text += f"Mean Reversion Results:\n"
            insights_text += f"• Sharpe Ratio: {best_mr['Sharpe_Ratio']:.3f}\n"
            insights_text += f"• Max Drawdown: {best_mr['Max_Drawdown']:.1%}\n"
            insights_text += f"• Parameters: {mr_best_params[0]}d window, {mr_best_params[1]:.1%} threshold\n\n"
            
            insights_text += f"Momentum Results:\n"
            insights_text += f"• Sharpe Ratio: {best_mom['Sharpe_Ratio']:.3f}\n"
            insights_text += f"• Max Drawdown: {best_mom['Max_Drawdown']:.1%}\n"
            insights_text += f"• Parameters: {mom_best_params}d window\n\n"
            
            insights_text += f"WINNER: {winning_strategy} Strategy\n\n"
            
            # AI-powered market behavior analysis
            insights_text += f"AI MARKET BEHAVIOR ANALYSIS\n\n"
            try:
                import ai_utils
                ai_analysis = ai_utils.generate_market_behavior_analysis(
                    self.ticker, winning_strategy, 
                    best_mr['Sharpe_Ratio'], best_mom['Sharpe_Ratio'],
                    mr_best_params, mom_best_params,
                    best_mr.get('Max_Drawdown'), best_mom.get('Max_Drawdown')
                )
                insights_text += ai_analysis
            except Exception as e:
                # Fallback to simple analysis
                insights_text += f"Analysis based on backtest results:\n"
                if winning_strategy == "Mean Reversion":
                    insights_text += f"• {self.ticker} showed mean-reverting characteristics\n"
                    insights_text += f"• Price movements tend to revert to average levels\n"
                    insights_text += f"• Counter-trend strategies were effective"
                else:
                    insights_text += f"• {self.ticker} demonstrated trending behavior\n"
                    insights_text += f"• Momentum strategies captured price trends\n"
                    insights_text += f"• Trend-following approach was more successful"
        
        # Clean up formatting and display text
        clean_text = insights_text.replace('**', '')  # Remove markdown bold markers
        ax.text(0.1, 0.85, clean_text, transform=ax.transAxes, fontsize=10,
                verticalalignment='top', fontfamily='serif', wrap=True)
        
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    
    def _create_glossary_page(self, pdf):
        """Create comprehensive glossary page with finance terms and formulas."""
        fig, ax = plt.subplots(figsize=(8.27, 11.69))  # A4 format
        ax.axis('off')
        
        # Title
        fig.suptitle('Financial Terms & Formulas Glossary', fontsize=14, fontweight='bold', y=0.92)
        
        glossary_text = """
TRADING STRATEGIES

Mean Reversion Strategy
• Concept: Assumes prices will return to their historical average over time
• Method: Buy when price is below moving average, sell when above
• Formula: Signal = (Price - Moving_Average) / Moving_Average
• Why useful: Captures price "overshoots" and corrections in sideways markets

Momentum Strategy  
• Concept: Assumes prices will continue moving in the same direction
• Method: Buy when price > moving average, sell when price < moving average
• Formula: Signal = Price - Moving_Average
• Why useful: Captures trending behavior and market momentum

PERFORMANCE METRICS

Sharpe Ratio
• Formula: (Portfolio_Return - Risk_Free_Rate) / Portfolio_Volatility
• Meaning: Risk-adjusted return measure
• Why important: Higher ratio = better return per unit of risk taken
• Interpretation: >1.0 is good, >2.0 is excellent

Maximum Drawdown
• Formula: (Peak_Value - Trough_Value) / Peak_Value
• Meaning: Largest peak-to-trough decline in portfolio value
• Why important: Measures worst-case scenario loss
• Interpretation: Lower is better (less risk)

Portfolio Value
• Formula: Initial_Capital × (1 + Cumulative_Returns)
• Meaning: Total value of investment over time
• Why useful: Shows actual dollar growth of investment

TECHNICAL PARAMETERS

Window Size
• Definition: Number of historical periods used for calculations
• Usage: Moving averages, volatility calculations
• Impact: Smaller = more sensitive, Larger = smoother signals
• Typical range: 10-50 days for short-term strategies

Threshold (Mean Reversion)
• Definition: Percentage deviation from average to trigger trades
• Formula: |Price - Moving_Average| / Moving_Average > Threshold
• Impact: Lower = more trades, Higher = fewer but stronger signals
• Typical range: 1%-5% for most assets

RISK CONCEPTS

Volatility
• Formula: Standard deviation of returns
• Meaning: Measure of price fluctuation intensity  
• Why important: Higher volatility = higher risk and potential return

Buy/Sell Signals
• Definition: Automated trading recommendations based on strategy rules
• Implementation: Generated when price crosses predetermined levels
• Purpose: Remove emotion and provide systematic entry/exit points
        """
        
        # Add glossary text with consistent font
        ax.text(0.1, 0.85, glossary_text, transform=ax.transAxes, fontsize=9,
                verticalalignment='top', fontfamily='serif')
        
        pdf.savefig(fig, dpi=150)
        plt.close(fig)
    


def prompt_for_report_generation(report_type, results=None, mr_results=None, mom_results=None, 
                                mr_best_params=None, mom_best_params=None, ticker=None):
    """Prompt user to generate PDF report and handle the generation."""
    try:
        generate = input(f"\nGenerate PDF report? (y/N): ").strip().lower()
        if generate in ['y', 'yes']:
            print("Generating PDF report...")
            
            report_gen = StrategyReportGenerator(ticker)
            
            if report_type == 'basic' and results:
                filename = report_gen.generate_basic_report(results)
            elif report_type == 'full' and mr_results and mom_results:
                filename = report_gen.generate_full_report(mr_results, mom_results, mr_best_params, mom_best_params)
            else:
                print("ERROR: Invalid report configuration")
                return
            
            print(f"PDF report generated: {filename}")
            
            # Check if file was created and show file size
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / 1024  # Size in KB
                print(f"Report saved successfully ({file_size:.1f} KB)")
            else:
                print("ERROR: Report file was not created")
                
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping report generation.")
    except Exception as e:
        print(f"ERROR generating report: {e}")