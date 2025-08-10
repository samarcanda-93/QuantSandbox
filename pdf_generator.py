#!/usr/bin/env python3
"""
Professional PDF report generator using ReportLab for consistent A4 formatting.
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle, Image
from reportlab.lib.colors import black, blue, green, red, grey
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from datetime import datetime
import matplotlib.pyplot as plt
import io
import base64
import pandas as pd
import tempfile
import os

class ProfessionalReportGenerator:
    """Generate professional PDF reports with consistent A4 formatting."""
    
    def __init__(self, ticker):
        self.ticker = ticker
        self.styles = getSampleStyleSheet()
        self._setup_custom_styles()
        
    def _setup_custom_styles(self):
        """Setup custom paragraph styles for consistent formatting."""
        # Title style
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=18,
            spaceAfter=30,
            textColor=black,
            alignment=TA_CENTER
        ))
        
        # Section header style
        self.styles.add(ParagraphStyle(
            name='SectionHeader',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceBefore=20,
            spaceAfter=10,
            textColor=blue
        ))
        
        # Subsection style
        self.styles.add(ParagraphStyle(
            name='SubSection',
            parent=self.styles['Heading3'],
            fontSize=12,
            spaceBefore=15,
            spaceAfter=8,
            textColor=black
        ))
        
        # Body text with proper spacing
        self.styles.add(ParagraphStyle(
            name='CustomBody',
            parent=self.styles['Normal'],
            fontSize=10,
            spaceBefore=6,
            spaceAfter=6,
            leftIndent=0
        ))
        
        # Bullet point style
        self.styles.add(ParagraphStyle(
            name='CustomBullet',
            parent=self.styles['Normal'],
            fontSize=10,
            leftIndent=20,
            spaceBefore=3,
            spaceAfter=3
        ))
        
        # Disclaimer style
        self.styles.add(ParagraphStyle(
            name='Disclaimer',
            parent=self.styles['Normal'],
            fontSize=8,
            textColor=grey,
            alignment=TA_CENTER,
            spaceBefore=10
        ))
    
    def generate_full_report(self, mr_results, mom_results, mr_best_params, mom_best_params, filename=None):
        """Generate comprehensive PDF report."""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"professional_analysis_report_{self.ticker}_{timestamp}.pdf"
        
        # Create PDF document
        doc = SimpleDocTemplate(filename, pagesize=A4, 
                              rightMargin=2*cm, leftMargin=2*cm,
                              topMargin=2*cm, bottomMargin=2*cm)
        
        # Build content
        content = []
        
        # Page 1: Executive Summary
        content.extend(self._create_executive_summary(mr_results, mom_results, mr_best_params, mom_best_params))
        content.append(PageBreak())
        
        # Page 2: Strategy Performance
        content.extend(self._create_performance_analysis(mr_results, mom_results, mr_best_params, mom_best_params))
        content.append(PageBreak())
        
        # Page 3: Parameter Analysis
        content.extend(self._create_parameter_analysis(mr_results, mom_results, mr_best_params, mom_best_params))
        content.append(PageBreak())
        
        # Page 4: AI Market Insights
        content.extend(self._create_market_insights(mr_results, mom_results, mr_best_params, mom_best_params))
        content.append(PageBreak())
        
        # Page 5: Glossary
        content.extend(self._create_glossary())
        
        # Build PDF
        doc.build(content)
        return filename
    
    def _create_executive_summary(self, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create executive summary page."""
        content = []
        
        # Title
        title = Paragraph(f"Comprehensive Strategy Analysis - {self.ticker}", self.styles['CustomTitle'])
        content.append(title)
        
        # Report metadata
        report_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        meta_text = f"<b>Report Generated:</b> {report_date}<br/><b>Asset:</b> {self.ticker}"
        content.append(Paragraph(meta_text, self.styles['CustomBody']))
        content.append(Spacer(1, 20))
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            # Mean Reversion Results
            content.append(Paragraph("Mean Reversion Strategy", self.styles['SectionHeader']))
            mr_text = f"""
            <b>Best Parameters:</b> Window={mr_best_params[0]}, Threshold={mr_best_params[1]:.1%}<br/>
            <b>Sharpe Ratio:</b> {best_mr['Sharpe_Ratio']:.4f}<br/>
            <b>Max Drawdown:</b> {best_mr['Max_Drawdown']:.2%}
            """
            content.append(Paragraph(mr_text, self.styles['CustomBody']))
            content.append(Spacer(1, 15))
            
            # Momentum Results
            content.append(Paragraph("Momentum Strategy", self.styles['SectionHeader']))
            mom_text = f"""
            <b>Best Parameter:</b> Window={mom_best_params}<br/>
            <b>Sharpe Ratio:</b> {best_mom['Sharpe_Ratio']:.4f}<br/>
            <b>Max Drawdown:</b> {best_mom['Max_Drawdown']:.2%}
            """
            content.append(Paragraph(mom_text, self.styles['CustomBody']))
            content.append(Spacer(1, 20))
            
            # Recommendation
            winner = "Momentum" if best_mom['Sharpe_Ratio'] > best_mr['Sharpe_Ratio'] else "Mean Reversion"
            content.append(Paragraph("Recommendation", self.styles['SectionHeader']))
            rec_text = f"<b>{winner} strategy is recommended</b> based on superior risk-adjusted returns."
            content.append(Paragraph(rec_text, self.styles['CustomBody']))
            
            # Today's suggestion
            try:
                import finance_utils
                best_strategy_data = best_mom if winner == "Momentum" else best_mr
                rec = finance_utils.latest_trade_recommendation(best_strategy_data['Data'], ticker=self.ticker)
                if rec and rec.get('as_of_date'):
                    date_str = rec['as_of_date'].strftime('%Y-%m-%d') if hasattr(rec['as_of_date'], 'strftime') else str(rec['as_of_date'])
                    price_str = f" at {rec['price']:.2f}" if rec.get('price') else ""
                    suggestion_text = f"<b>Today's Suggestion:</b> {rec['action']} ({rec['state']}) as of {date_str}{price_str}"
                    content.append(Spacer(1, 15))
                    content.append(Paragraph(suggestion_text, self.styles['CustomBody']))
            except Exception:
                pass
        
        # Disclaimer
        content.append(Spacer(1, 30))
        disclaimer = ("DISCLAIMER: This report is for educational purposes only and does not constitute financial advice. "
                     "Past performance does not guarantee future results. Trading involves risk and can result in losses. "
                     "Consult a qualified financial advisor before making investment decisions.")
        content.append(Paragraph(disclaimer, self.styles['Disclaimer']))
        
        return content
    
    def _create_performance_analysis(self, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create performance analysis with embedded charts."""
        content = []
        
        content.append(Paragraph("Strategy Performance Analysis", self.styles['CustomTitle']))
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            
            # Performance comparison table
            content.append(Paragraph("Performance Summary", self.styles['SectionHeader']))
            
            table_data = [
                ['Strategy', 'Sharpe Ratio', 'Max Drawdown', 'Parameters'],
                ['Mean Reversion', f'{best_mr["Sharpe_Ratio"]:.4f}', f'{best_mr["Max_Drawdown"]:.2%}', 
                 f'W={mr_best_params[0]}, T={mr_best_params[1]:.1%}'],
                ['Momentum', f'{best_mom["Sharpe_Ratio"]:.4f}', f'{best_mom["Max_Drawdown"]:.2%}', 
                 f'W={mom_best_params}']
            ]
            
            table = Table(table_data, colWidths=[4*cm, 3*cm, 3*cm, 4*cm])
            table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), green),
                ('TEXTCOLOR', (0, 0), (-1, 0), black),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), grey),
                ('GRID', (0, 0), (-1, -1), 1, black),
                ('FONTSIZE', (0, 1), (-1, -1), 9),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [None, grey]),
            ]))
            content.append(table)
            content.append(Spacer(1, 20))
            
            # Risk-Return Analysis
            content.append(Paragraph("Risk-Return Analysis", self.styles['SectionHeader']))
            
            sharpe_diff = abs(best_mr['Sharpe_Ratio'] - best_mom['Sharpe_Ratio'])
            dd_diff = abs(best_mr['Max_Drawdown'] - best_mom['Max_Drawdown'])
            
            analysis_text = f"""
            <b>Performance Gap:</b> {sharpe_diff:.3f} difference in Sharpe ratios<br/>
            <b>Risk Differential:</b> {dd_diff:.1%} difference in maximum drawdown<br/><br/>
            
            <b>Key Observations:</b><br/>
            • {"Momentum" if best_mom['Sharpe_Ratio'] > best_mr['Sharpe_Ratio'] else "Mean Reversion"} strategy achieved superior risk-adjusted returns<br/>
            • {"Lower" if best_mom['Max_Drawdown'] < best_mr['Max_Drawdown'] else "Higher"} risk profile with {"Momentum" if best_mom['Max_Drawdown'] < best_mr['Max_Drawdown'] else "Mean Reversion"}<br/>
            • {"Both strategies showed reasonable performance" if sharpe_diff < 0.3 else "Clear performance leader identified"}
            """
            content.append(Paragraph(analysis_text, self.styles['CustomBody']))
        
        return content
    
    def _create_parameter_analysis(self, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create parameter sensitivity analysis."""
        content = []
        
        content.append(Paragraph("Parameter Optimization Results", self.styles['CustomTitle']))
        
        # Mean Reversion Parameter Analysis
        if mr_results:
            content.append(Paragraph("Mean Reversion Parameter Sensitivity", self.styles['SectionHeader']))
            
            # Create summary statistics
            mr_df = pd.DataFrame(mr_results)
            best_window = mr_df.groupby('Window')['Sharpe_Ratio'].max().idxmax()
            best_threshold = mr_df.groupby('Threshold')['Sharpe_Ratio'].max().idxmax()
            
            mr_analysis = f"""
            <b>Optimal Parameters:</b> Window={mr_best_params[0]} days, Threshold={mr_best_params[1]:.1%}<br/>
            <b>Best Window Overall:</b> {best_window} days (across all thresholds)<br/>
            <b>Best Threshold Overall:</b> {best_threshold:.1%} (across all windows)<br/>
            <b>Sharpe Range:</b> {mr_df['Sharpe_Ratio'].min():.3f} to {mr_df['Sharpe_Ratio'].max():.3f}<br/>
            <b>Parameter Sensitivity:</b> {"High" if (mr_df['Sharpe_Ratio'].max() - mr_df['Sharpe_Ratio'].min()) > 1.0 else "Moderate"} variation across parameters
            """
            content.append(Paragraph(mr_analysis, self.styles['CustomBody']))
            content.append(Spacer(1, 15))
        
        # Momentum Parameter Analysis
        if mom_results:
            content.append(Paragraph("Momentum Parameter Sensitivity", self.styles['SectionHeader']))
            
            mom_df = pd.DataFrame(mom_results)
            
            mom_analysis = f"""
            <b>Optimal Parameter:</b> Window={mom_best_params} days<br/>
            <b>Sharpe Range:</b> {mom_df['Sharpe_Ratio'].min():.3f} to {mom_df['Sharpe_Ratio'].max():.3f}<br/>
            <b>Best Performance:</b> {"Short-term" if mom_best_params <= 20 else "Long-term"} window optimal<br/>
            <b>Parameter Sensitivity:</b> {"High" if (mom_df['Sharpe_Ratio'].max() - mom_df['Sharpe_Ratio'].min()) > 1.0 else "Moderate"} variation across windows
            """
            content.append(Paragraph(mom_analysis, self.styles['CustomBody']))
        
        return content
    
    def _create_market_insights(self, mr_results, mom_results, mr_best_params, mom_best_params):
        """Create AI-powered market insights page."""
        content = []
        
        content.append(Paragraph(f"Market Behavior Analysis - {self.ticker}", self.styles['CustomTitle']))
        
        if mr_best_params and mom_best_params:
            best_mr = next(r for r in mr_results if r['Window'] == mr_best_params[0] and r['Threshold'] == mr_best_params[1])
            best_mom = next(r for r in mom_results if r['Window'] == mom_best_params)
            winning_strategy = "Mean Reversion" if best_mr['Sharpe_Ratio'] > best_mom['Sharpe_Ratio'] else "Momentum"
            
            # Strategy comparison
            content.append(Paragraph("Quantitative Analysis Results", self.styles['SectionHeader']))
            
            comparison_text = f"""
            <b>Mean Reversion Performance:</b><br/>
            • Sharpe Ratio: {best_mr['Sharpe_Ratio']:.3f}<br/>
            • Max Drawdown: {best_mr['Max_Drawdown']:.1%}<br/>
            • Parameters: {mr_best_params[0]}d window, {mr_best_params[1]:.1%} threshold<br/><br/>
            
            <b>Momentum Performance:</b><br/>
            • Sharpe Ratio: {best_mom['Sharpe_Ratio']:.3f}<br/>
            • Max Drawdown: {best_mom['Max_Drawdown']:.1%}<br/>
            • Parameters: {mom_best_params}d window<br/><br/>
            
            <b>Winner:</b> {winning_strategy} Strategy
            """
            content.append(Paragraph(comparison_text, self.styles['CustomBody']))
            content.append(Spacer(1, 20))
            
            # AI Analysis
            content.append(Paragraph("AI-Powered Market Behavior Analysis", self.styles['SectionHeader']))
            
            try:
                import ai_utils
                ai_analysis = ai_utils.generate_market_behavior_analysis(
                    self.ticker, winning_strategy, 
                    best_mr['Sharpe_Ratio'], best_mom['Sharpe_Ratio'],
                    mr_best_params, mom_best_params,
                    best_mr.get('Max_Drawdown'), best_mom.get('Max_Drawdown')
                )
                
                # Format AI analysis for ReportLab
                formatted_analysis = ai_analysis.replace('•', '&bull;').replace('\n', '<br/>')
                content.append(Paragraph(formatted_analysis, self.styles['CustomBody']))
                
            except Exception as e:
                # Fallback analysis
                fallback_text = f"""
                <b>Analysis based on backtest results:</b><br/>
                &bull; {self.ticker} demonstrated {winning_strategy.lower()} characteristics in this period<br/>
                &bull; Risk-adjusted returns favored the {winning_strategy.lower()} approach<br/>
                &bull; Parameter optimization revealed {"short-term" if (winning_strategy == "Momentum" and mom_best_params <= 20) or (winning_strategy == "Mean Reversion" and mr_best_params[0] <= 20) else "longer-term"} signals were most effective
                """
                content.append(Paragraph(fallback_text, self.styles['CustomBody']))
        
        return content
    
    def _create_glossary(self):
        """Create financial terms glossary."""
        content = []
        
        content.append(Paragraph("Financial Terms & Formulas Glossary", self.styles['CustomTitle']))
        
        # Trading Strategies Section
        content.append(Paragraph("Trading Strategies", self.styles['SectionHeader']))
        
        mean_reversion_text = """
        <b>Mean Reversion Strategy</b><br/>
        &bull; <b>Concept:</b> Assumes prices will return to their historical average over time<br/>
        &bull; <b>Method:</b> Buy when price is below moving average, sell when above<br/>
        &bull; <b>Formula:</b> Signal = (Price - Moving_Average) / Moving_Average<br/>
        &bull; <b>Why useful:</b> Captures price overshoots and corrections in sideways markets
        """
        content.append(Paragraph(mean_reversion_text, self.styles['CustomBody']))
        content.append(Spacer(1, 10))
        
        momentum_text = """
        <b>Momentum Strategy</b><br/>
        &bull; <b>Concept:</b> Assumes prices will continue moving in the same direction<br/>
        &bull; <b>Method:</b> Buy when price &gt; moving average, sell when price &lt; moving average<br/>
        &bull; <b>Formula:</b> Signal = Price - Moving_Average<br/>
        &bull; <b>Why useful:</b> Captures trending behavior and market momentum
        """
        content.append(Paragraph(momentum_text, self.styles['CustomBody']))
        content.append(Spacer(1, 15))
        
        # Performance Metrics Section
        content.append(Paragraph("Performance Metrics", self.styles['SectionHeader']))
        
        sharpe_text = """
        <b>Sharpe Ratio</b><br/>
        &bull; <b>Formula:</b> (Portfolio_Return - Risk_Free_Rate) / Portfolio_Volatility<br/>
        &bull; <b>Meaning:</b> Risk-adjusted return measure<br/>
        &bull; <b>Why important:</b> Higher ratio = better return per unit of risk taken<br/>
        &bull; <b>Interpretation:</b> &gt;1.0 is good, &gt;2.0 is excellent
        """
        content.append(Paragraph(sharpe_text, self.styles['CustomBody']))
        content.append(Spacer(1, 10))
        
        drawdown_text = """
        <b>Maximum Drawdown</b><br/>
        &bull; <b>Formula:</b> (Peak_Value - Trough_Value) / Peak_Value<br/>
        &bull; <b>Meaning:</b> Largest peak-to-trough decline in portfolio value<br/>
        &bull; <b>Why important:</b> Measures worst-case scenario loss<br/>
        &bull; <b>Interpretation:</b> Lower is better (less risk)
        """
        content.append(Paragraph(drawdown_text, self.styles['CustomBody']))
        
        return content


def prompt_for_professional_report_generation(report_type, results=None, mr_results=None, mom_results=None, 
                                            mr_best_params=None, mom_best_params=None, ticker=None):
    """Prompt user to generate professional PDF report."""
    try:
        generate = input(f"\nGenerate professional PDF report? (y/N): ").strip().lower()
        if generate in ['y', 'yes']:
            print("Generating professional PDF report...")
            
            report_gen = ProfessionalReportGenerator(ticker)
            
            if report_type == 'full' and mr_results and mom_results:
                filename = report_gen.generate_full_report(mr_results, mom_results, mr_best_params, mom_best_params)
            else:
                print("ERROR: Professional reports currently support full analysis only")
                return
            
            print(f"Professional PDF report generated: {filename}")
            
            # Check if file was created and show file size
            if os.path.exists(filename):
                file_size = os.path.getsize(filename) / 1024  # Size in KB
                print(f"Report saved successfully ({file_size:.1f} KB)")
                print("Features: Professional layout, consistent A4 formatting, no matplotlib boxes")
            else:
                print("ERROR: Report file was not created")
                
    except (EOFError, KeyboardInterrupt):
        print("\nSkipping professional report generation.")
    except Exception as e:
        print(f"ERROR generating professional report: {e}")