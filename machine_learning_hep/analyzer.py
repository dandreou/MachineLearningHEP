#############################################################################
##  © Copyright CERN 2018. All rights not expressly granted are reserved.  ##
##                 Author: Gian.Michele.Innocenti@cern.ch                  ##
## This program is free software: you can redistribute it and/or modify it ##
##  under the terms of the GNU General Public License as published by the  ##
## Free Software Foundation, either version 3 of the License, or (at your  ##
## option) any later version. This program is distributed in the hope that ##
##  it will be useful, but WITHOUT ANY WARRANTY; without even the implied  ##
##     warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.    ##
##           See the GNU General Public License for more details.          ##
##    You should have received a copy of the GNU General Public License    ##
##   along with this program. if not, see <https://www.gnu.org/licenses/>. ##
#############################################################################

"""
main script for doing final stage analysis
"""
import os
# pylint: disable=unused-wildcard-import, wildcard-import
from array import *
# pylint: disable=import-error, no-name-in-module, unused-import
from ROOT import TFile, TH1F, TCanvas
from ROOT import gStyle, TLegend
from ROOT import gROOT
from ROOT import TStyle
from ROOT import TLatex
from machine_learning_hep.globalfitter import fitter

# pylint: disable=too-few-public-methods, too-many-instance-attributes, too-many-statements
class Analyzer:
    species = "analyzer"
    def __init__(self, datap, case, typean):


        #namefiles pkl
        self.case = case
        self.typean = typean
        self.v_var_binning = datap["var_binning"]
        self.lpt_finbinmin = datap["analysis"][self.typean]["sel_an_binmin"]
        self.lpt_finbinmax = datap["analysis"][self.typean]["sel_an_binmax"]
        self.bin_matching = datap["analysis"][self.typean]["binning_matching"]
        self.p_nptbins = len(self.lpt_finbinmin)
        self.lpt_probcutfin = datap["mlapplication"]["probcutoptimal"]

        self.lvar2_binmin = datap["analysis"][self.typean]["sel_binmin2"]
        self.lvar2_binmax = datap["analysis"][self.typean]["sel_binmax2"]
        self.v_var2_binning = datap["analysis"][self.typean]["var_binning2"]
        self.p_nbin2 = len(self.lvar2_binmin)

        self.d_resultsallpmc = datap["analysis"][self.typean]["mc"]["resultsallp"]
        self.d_resultsallpdata = datap["analysis"][self.typean]["data"]["resultsallp"]

        self.n_filemass = datap["files_names"]["histofilename"]
        self.n_filemass = os.path.join(self.d_resultsallpdata, self.n_filemass)
        self.n_filecross = datap["files_names"]["crossfilename"]
        self.p_mass_fit_lim = datap["analysis"][self.typean]['mass_fit_lim']

        self.n_fileff = datap["files_names"]["efffilename"]
        self.n_fileff = os.path.join(self.d_resultsallpmc, self.n_fileff)
        self.n_evtvalroot = datap["files_names"]["namefile_evtvalroot"]

        self.p_bin_width = datap["analysis"][self.typean]['bin_width']
        self.p_num_bins = int(round((self.p_mass_fit_lim[1] - self.p_mass_fit_lim[0]) / \
                                    self.p_bin_width))
        #parameter fitter
        self.p_sgnfunc = datap["analysis"][self.typean]["sgnfunc"]
        self.p_bkgfunc = datap["analysis"][self.typean]["bkgfunc"]
        self.p_masspeak = datap["analysis"][self.typean]["masspeak"]
        self.p_massmin = datap["analysis"][self.typean]["massmin"]
        self.p_massmax = datap["analysis"][self.typean]["massmax"]
        self.p_rebin = datap["analysis"][self.typean]["rebin"]
        self.p_includesecpeak = datap["analysis"][self.typean]["includesecpeak"]
        self.p_masssecpeak = datap["analysis"][self.typean]["masssecpeak"]
        self.p_fixedmean = datap["analysis"][self.typean]["FixedMean"]
        self.p_fixingaussigma = datap["analysis"][self.typean]["SetFixGaussianSigma"]
        self.p_fixingausmean = datap["analysis"][self.typean]["SetInitialGaussianMean"]
        self.p_dolike = datap["analysis"][self.typean]["dolikelihood"]
        self.p_sigmaarray = datap["analysis"][self.typean]["sigmaarray"]
        self.p_fixedsigma = datap["analysis"][self.typean]["FixedSigma"]
        self.p_casefit = datap["analysis"][self.typean]["fitcase"]
        self.p_latexnmeson = datap["analysis"][self.typean]["latexnamemeson"]
        self.p_latexbin2var = datap["analysis"][self.typean]["latexbin2var"]
        self.p_dofullevtmerge = datap["dofullevtmerge"]
        self.p_dodoublecross = datap["analysis"][self.typean]["dodoublecross"]
        self.ptranges = self.lpt_finbinmin.copy()
        self.ptranges.append(self.lpt_finbinmax[-1])
        self.var2ranges = self.lvar2_binmin.copy()
        self.var2ranges.append(self.lvar2_binmax[-1])
        print(self.var2ranges)
        self.lmult_yieldshisto = [TH1F("hyields%d" % (imult), "", \
            self.p_nptbins, array("d", self.ptranges)) for imult in range(self.p_nbin2)]

        self.p_nevents = datap["analysis"][self.typean]["nevents"]
        self.p_bineff = datap["analysis"][self.typean]["usesinglebineff"]
        self.p_sigmamb = datap["ml"]["opt"]["sigma_MB"]
        self.p_br = datap["ml"]["opt"]["BR"]

        self.d_valevtdata = datap["validation"]["data"]["dirmerged"]
        self.d_valevtmc = datap["validation"]["mc"]["dirmerged"]
        self.f_evtvaldata = os.path.join(self.d_valevtdata, self.n_evtvalroot)
        self.f_evtvalmc = os.path.join(self.d_valevtmc, self.n_evtvalroot)

    @staticmethod
    def loadstyle():
        gROOT.SetStyle("Plain")
        gStyle.SetOptStat(0)
        gStyle.SetOptStat(0000)
        gStyle.SetPalette(0)
        gStyle.SetCanvasColor(0)
        gStyle.SetFrameFillColor(0)
        gStyle.SetOptTitle(0)

    def fitter(self):
        self.loadstyle()
        lfile = TFile.Open(self.n_filemass)
        fileout = TFile.Open("%s/yields%s%s.root" % (self.d_resultsallpdata,
                                                     self.case, self.typean), "recreate")
        for imult in range(self.p_nbin2):
            for ipt in range(self.p_nptbins):
                bin_id = self.bin_matching[ipt]
                suffix = "%s%d_%d_%.2f%s_%.2f_%.2f" % \
                         (self.v_var_binning, self.lpt_finbinmin[ipt],
                          self.lpt_finbinmax[ipt], self.lpt_probcutfin[bin_id],
                          self.v_var2_binning, self.lvar2_binmin[imult], self.lvar2_binmax[imult])
                h_invmass = lfile.Get("hmass" + suffix)
                rawYield, rawYieldErr, sig_fit, bkg_fit = \
                    fitter(h_invmass, self.p_casefit, self.p_sgnfunc[ipt], self.p_bkgfunc[ipt], \
                    self.p_masspeak, self.p_rebin[ipt], self.p_dolike, self.p_fixingausmean, \
                    self.p_fixingaussigma, self.p_sigmaarray[ipt], self.p_massmin[ipt], \
                    self.p_massmax[ipt], self.p_fixedmean, self.d_resultsallpdata, suffix)
                fileout.cd()
                sig_fit.SetName("sigfit" + suffix)
                sig_fit.Write("sigfit" + suffix)
                bkg_fit.SetName("bkgfit" + suffix)
                bkg_fit.Write("bkgfit" + suffix)
                rawYield = rawYield/(self.lpt_finbinmax[ipt] - self.lpt_finbinmin[ipt])
                rawYieldErr = rawYieldErr/(self.lpt_finbinmax[ipt] - self.lpt_finbinmin[ipt])
                self.lmult_yieldshisto[imult].SetBinContent(ipt + 1, rawYield)
                self.lmult_yieldshisto[imult].SetBinError(ipt + 1, rawYieldErr)
            fileout.cd()
            self.lmult_yieldshisto[imult].Write()
        fileout.Close()
        cYields = TCanvas('cYields', 'The Fit Canvas')
        cYields.SetCanvasSize(1900, 1500)
        cYields.SetWindowSize(500, 500)
        cYields.SetLogy()

        legyield = TLegend(.5, .65, .7, .85)
        legyield.SetBorderSize(0)
        legyield.SetFillColor(0)
        legyield.SetFillStyle(0)
        legyield.SetTextFont(42)
        legyield.SetTextSize(0.035)

        lfile = TFile.Open("%s/yields%s%s.root" % (self.d_resultsallpdata,
                                                   self.case, self.typean))
        for imult in range(self.p_nbin2):
            self.lmult_yieldshisto[imult].SetMinimum(1)
            self.lmult_yieldshisto[imult].SetMaximum(1e6)
            self.lmult_yieldshisto[imult].SetLineColor(imult+1)
            self.lmult_yieldshisto[imult].Draw("same")
            legyieldstring = "%.1f < %s < %.1f GeV/c" % \
                    (self.lvar2_binmin[imult], self.p_latexbin2var, self.lvar2_binmax[imult])
            legyield.AddEntry(self.lmult_yieldshisto[imult], legyieldstring, "LEP")
            self.lmult_yieldshisto[imult].GetXaxis().SetTitle("p_{T} (GeV)")
            self.lmult_yieldshisto[imult].GetYaxis().SetTitle("Uncorrected yields %s %s (1/GeV)" \
                    % (self.p_latexnmeson, self.typean))

        legyield.Draw()
        cYields.SaveAs("%s/Yields%s%s.eps" % (self.d_resultsallpdata,
                                              self.case, self.typean))
        lfile.Close()
    def efficiency(self):
        self.loadstyle()

        lfileeff = TFile.Open(self.n_fileff)
        fileouteff = TFile.Open("%s/efficiencies%s%s.root" % (self.d_resultsallpmc, \
                                 self.case, self.typean), "recreate")
        cEff = TCanvas('cEff', 'The Fit Canvas')
        cEff.SetCanvasSize(1900, 1500)
        cEff.SetWindowSize(500, 500)

        legeff = TLegend(.5, .65, .7, .85)
        legeff.SetBorderSize(0)
        legeff.SetFillColor(0)
        legeff.SetFillStyle(0)
        legeff.SetTextFont(42)
        legeff.SetTextSize(0.035)

        for imult in range(self.p_nbin2):
            stringbin2 = "_%s_%.2f_%.2f" % (self.v_var2_binning, \
                                            self.lvar2_binmin[imult], \
                                            self.lvar2_binmax[imult])
            h_gen_pr = lfileeff.Get("h_gen_pr" + stringbin2)
            h_sel_pr = lfileeff.Get("h_sel_pr" + stringbin2)
            h_gen_fd = lfileeff.Get("h_gen_fd" + stringbin2)
            h_sel_fd = lfileeff.Get("h_sel_fd" + stringbin2)

            h_sel_pr.Divide(h_sel_pr, h_gen_pr, 1.0, 1.0, "B")
            h_sel_fd.Divide(h_sel_fd, h_gen_fd, 1.0, 1.0, "B")
            h_sel_pr.SetLineColor(imult+1)
            h_sel_pr.Draw("same")
            fileouteff.cd()
            h_sel_pr.SetName("eff_mult%d" % imult)
            h_sel_pr.Write()
            h_sel_fd.SetName("eff_fd_mult%d" % imult)
            h_sel_fd.Write()
            legeffstring = "%.1f < %s < %.1f GeV/c" % \
                    (self.lvar2_binmin[imult], self.p_latexbin2var, self.lvar2_binmax[imult])
            legeff.AddEntry(h_sel_pr, legeffstring, "LEP")
            h_sel_pr.GetXaxis().SetTitle("p_{T} (GeV)")
            h_sel_pr.GetYaxis().SetTitle("Uncorrected yields %s %s (1/GeV)" \
                    % (self.p_latexnmeson, self.typean))
            h_sel_pr.SetMinimum(0.)
            h_sel_pr.SetMaximum(1.5)
        legeff.Draw()
        cEff.SaveAs("%s/Eff%s%s.eps" % (self.d_resultsallpmc,
                                        self.case, self.typean))

    # pylint: disable=too-many-locals
    def side_band_sub(self):
        self.loadstyle()
        lfile = TFile.Open(self.n_filemass)
        func_file = TFile.Open("%s/yields%s%s.root" % \
                               (self.d_resultsallpdata, self.case, self.typean))
        eff_file = TFile.Open("%s/efficiencies%s%s.root" % \
                              (self.d_resultsallpmc, self.case, self.typean))
        fileouts = TFile.Open("%s/side_band_sub%s%s.root" % \
                              (self.d_resultsallpdata, self.case, self.typean), "recreate")
        for imult in range(self.p_nbin2):
            heff = eff_file.Get("eff_mult%d" % imult)
            hz = None
            for ipt in range(self.p_nptbins):
                bin_id = self.bin_matching[ipt]
                suffix = "%s%d_%d_%.2f%s_%.2f_%.2f" % \
                         (self.v_var_binning, self.lpt_finbinmin[ipt],
                          self.lpt_finbinmax[ipt], self.lpt_probcutfin[bin_id],
                          self.v_var2_binning, self.lvar2_binmin[imult], self.lvar2_binmax[imult])
                hzvsmass = lfile.Get("hzvsmass" + suffix)
                sig_fit = func_file.Get("sigfit" + suffix)
                mean = sig_fit.GetParameter(1)
                sigma = sig_fit.GetParameter(2)
                binmasslow2sig = hzvsmass.GetXaxis().FindBin(mean - 2*sigma)
                masslow2sig = mean - 2*sigma
                binmasshigh2sig = hzvsmass.GetXaxis().FindBin(mean + 2*sigma)
                masshigh2sig = mean + 2*sigma
                binmasslow4sig = hzvsmass.GetXaxis().FindBin(mean - 4*sigma)
                masslow4sig = mean - 4*sigma
                binmasshigh4sig = hzvsmass.GetXaxis().FindBin(mean + 4*sigma)
                masshigh4sig = mean + 4*sigma
                binmasslow9sig = hzvsmass.GetXaxis().FindBin(mean - 9*sigma)
                masslow9sig = mean - 9*sigma
                binmasshigh9sig = hzvsmass.GetXaxis().FindBin(mean + 9*sigma)
                masshigh9sig = mean + 9*sigma

                hzsig = hzvsmass.ProjectionY("hzsig" + suffix, \
                             binmasslow2sig, binmasshigh2sig, "e")
                hzsig.Rebin(100)
                hzbkgleft = hzvsmass.ProjectionY("hzbkgleft" + suffix, \
                             binmasslow9sig, binmasslow4sig, "e")
                hzbkgleft.Rebin(100)
                hzbkgright = hzvsmass.ProjectionY("hzbkgright" + suffix, \
                             binmasshigh4sig, binmasshigh9sig, "e")
                hzbkgright.Rebin(100)
                hzbkg = hzbkgleft.Clone("hzbkg" + suffix)
                hzbkg.Add(hzbkgright)
                bkg_fit = func_file.Get("bkgfit" + suffix)
                area_scale_denominator = bkg_fit.Integral(masslow9sig, masslow4sig) + \
                bkg_fit.Integral(masshigh4sig, masshigh9sig)
                area_scale = bkg_fit.Integral(masslow2sig, masshigh2sig)/area_scale_denominator
                hzsub = hzsig.Clone("hzsub" + suffix)
                hzsub.Add(hzbkg, -1*area_scale)
                eff = heff.GetBinContent(ipt+1)
                hzsub.Scale(1.0/(eff*0.9545))
                if ipt == 0:
                    hz = hzsub.Clone("hz")
                else:
                    hz.Add(hzsub)
                fileouts.cd()
                hzsig.Write()
                hzbkgleft.Write()
                hzbkgright.Write()
                hzbkg.Write()
                hzsub.Write()
                hz.Write()
                cside = TCanvas('cside' + suffix, 'The Fit Canvas')
                cside.SetCanvasSize(1900, 1500)
                cside.SetWindowSize(500, 500)
                hzvsmass.Draw("colz")

                cside.SaveAs("%s/zvsInvMass%s%s_%s.eps" % (self.d_resultsallpdata,
                                                           self.case, self.typean, suffix))

                csubsig = TCanvas('csubsig' + suffix, 'The Side-Band Sub Signal Canvas')
                csubsig.SetCanvasSize(1900, 1500)
                csubsig.SetWindowSize(500, 500)
                hzsig.Draw()

                csubsig.SaveAs("%s/side_band_sub_signal%s%s_%s.eps" % \
                               (self.d_resultsallpdata, self.case, self.typean, suffix))

                csubbkg = TCanvas('csubbkg' + suffix, 'The Side-Band Sub Background Canvas')
                csubbkg.SetCanvasSize(1900, 1500)
                csubbkg.SetWindowSize(500, 500)
                hzbkg.Draw()

                csubbkg.SaveAs("%s/side_band_sub_background%s%s_%s.eps" % \
                               (self.d_resultsallpdata, self.case, self.typean, suffix))

                csubz = TCanvas('csubz' + suffix, 'The Side-Band Sub Canvas')
                csubz.SetCanvasSize(1900, 1500)
                csubz.SetWindowSize(500, 500)
                hzsub.Draw()

                csubz.SaveAs("%s/side_band_sub%s%s_%s.eps" % \
                             (self.d_resultsallpdata, self.case, self.typean, suffix))
            cz = TCanvas('cz' + suffix, 'The Efficiency Corrected Signal Yield Canvas')
            cz.SetCanvasSize(1900, 1500)
            cz.SetWindowSize(500, 500)
            hz.Draw()

            cz.SaveAs("%s/side_band_sub%s%s_%s_%.2f_%.2f.eps" % \
                      (self.d_resultsallpdata, self.case, self.typean, self.v_var2_binning, \
                       self.lvar2_binmin[imult], self.lvar2_binmax[imult]))
        fileouts.Close()
    def plotter(self):
        self.loadstyle()

        fileouteff = TFile.Open("%s/efficiencies%s%s.root" % \
                                (self.d_resultsallpmc, self.case, self.typean))
        fileoutyield = TFile.Open("%s/yields%s%s.root" % \
                                  (self.d_resultsallpdata, self.case, self.typean))
        fileoutcross = TFile.Open("%s/finalcross%s%s.root" % \
                                  (self.d_resultsallpdata, self.case, self.typean), "recreate")

        cCrossvsvar1 = TCanvas('cCrossvsvar1', 'The Fit Canvas')
        cCrossvsvar1.SetCanvasSize(1900, 1500)
        cCrossvsvar1.SetWindowSize(500, 500)
        cCrossvsvar1.SetLogy()

        legvsvar1 = TLegend(.5, .65, .7, .85)
        legvsvar1.SetBorderSize(0)
        legvsvar1.SetFillColor(0)
        legvsvar1.SetFillStyle(0)
        legvsvar1.SetTextFont(42)
        legvsvar1.SetTextSize(0.035)

        listvalues = []
        listvalueserr = []

        for imult in range(self.p_nbin2):
            listvalpt = []
            bineff = -1
            if self.p_bineff is None:
                bineff = imult
                print("Using efficiency for each var2 bin")
            else:
                bineff = self.p_bineff
                print("Using efficiency always from bin=", bineff)
            heff = fileouteff.Get("eff_mult%d" % (bineff))
            hcross = fileoutyield.Get("hyields%d" % (imult))
            hcross.Divide(heff)
            hcross.SetLineColor(imult+1)
            norm = 2 * self.p_br * self.p_nevents / (self.p_sigmamb * 1e12)
            hcross.Scale(1./norm)
            fileoutcross.cd()
            hcross.GetXaxis().SetTitle("p_{T} %s (GeV)" % self.p_latexnmeson)
            hcross.GetYaxis().SetTitle("d#sigma/dp_{T} (%s) %s" %
                                       (self.p_latexnmeson, self.typean))
            hcross.SetName("hcross%d" % imult)
            hcross.GetYaxis().SetRangeUser(1e1, 1e10)
            legvsvar1endstring = "%.1f < %s < %.1f GeV/c" % \
                    (self.lvar2_binmin[imult], self.p_latexbin2var, self.lvar2_binmax[imult])
            legvsvar1.AddEntry(hcross, legvsvar1endstring, "LEP")
            hcross.Draw("same")
            hcross.Write()
            listvalpt = [hcross.GetBinContent(ipt+1) for ipt in range(self.p_nptbins)]
            listvalues.append(listvalpt)
            listvalerrpt = [hcross.GetBinError(ipt+1) for ipt in range(self.p_nptbins)]
            listvalueserr.append(listvalerrpt)
        legvsvar1.Draw()
        cCrossvsvar1.SaveAs("%s/Cross%s%sVs%s.eps" % (self.d_resultsallpdata,
                                                      self.case, self.typean, self.v_var_binning))

        cCrossvsvar2 = TCanvas('cCrossvsvar2', 'The Fit Canvas')
        cCrossvsvar2.SetCanvasSize(1900, 1500)
        cCrossvsvar2.SetWindowSize(500, 500)
        cCrossvsvar2.SetLogy()

        legvsvar2 = TLegend(.5, .65, .7, .85)
        legvsvar2.SetBorderSize(0)
        legvsvar2.SetFillColor(0)
        legvsvar2.SetFillStyle(0)
        legvsvar2.SetTextFont(42)
        legvsvar2.SetTextSize(0.035)
        hcrossvsvar2 = [TH1F("hcrossvsvar2" + "pt%d" % ipt, "", \
                        self.p_nbin2, array("d", self.var2ranges)) \
                        for ipt in range(self.p_nptbins)]

        for ipt in range(self.p_nptbins):
            print("pt", ipt)
            for imult in range(self.p_nbin2):
                hcrossvsvar2[ipt].SetLineColor(ipt+1)
                hcrossvsvar2[ipt].GetXaxis().SetTitle("%s" % self.p_latexbin2var)
                hcrossvsvar2[ipt].GetYaxis().SetTitle(self.p_latexnmeson)
                binmulrange = self.var2ranges[imult+1]-self.var2ranges[imult]
                if self.p_dodoublecross is True:
                    hcrossvsvar2[ipt].SetBinContent(imult+1, listvalues[imult][ipt]/binmulrange)
                    hcrossvsvar2[ipt].SetBinError(imult+1, listvalueserr[imult][ipt]/binmulrange)
                else:
                    hcrossvsvar2[ipt].SetBinContent(imult+1, listvalues[imult][ipt])
                    hcrossvsvar2[ipt].SetBinError(imult+1, listvalueserr[imult][ipt])

                hcrossvsvar2[ipt].GetYaxis().SetRangeUser(1e4, 1e10)
            legvsvar2endstring = "%.1f < %s < %.1f GeV/c" % \
                    (self.lpt_finbinmin[ipt], "p_{T}", self.lpt_finbinmax[ipt])
            hcrossvsvar2[ipt].Draw("same")
            legvsvar2.AddEntry(hcrossvsvar2[ipt], legvsvar2endstring, "LEP")
        legvsvar2.Draw()
        cCrossvsvar2.SaveAs("%s/Cross%s%sVs%s.eps" % (self.d_resultsallpdata,
                                                      self.case, self.typean, self.v_var2_binning))

    def studyevents(self):
        self.loadstyle()

        filedata = TFile.Open(self.f_evtvaldata)
        filemc = TFile.Open(self.f_evtvalmc)
        v0mn_trackletsdata = filedata.Get("v0mn_tracklets")
        v0mn_trackletsmc = filemc.Get("v0mn_tracklets")

        cscatter = TCanvas('cscatter', 'The Fit Canvas')
        cscatter.SetCanvasSize(1900, 1000)
        cscatter.Divide(2, 1)
        cscatter.cd(1)
        v0mn_trackletsdata.GetXaxis().SetTitle("offline V0 (data)")
        v0mn_trackletsdata.GetYaxis().SetTitle("offline SPD (data)")
        v0mn_trackletsdata.Draw("colz")
        cscatter.cd(2)
        v0mn_trackletsmc.GetXaxis().SetTitle("offline V0 (mc)")
        v0mn_trackletsmc.GetYaxis().SetTitle("offline SPD (mc)")
        v0mn_trackletsmc.Draw("colz")
        cscatter.SaveAs("cscatter.pdf")

        labelsv0 = ["kINT7_vsv0m", "HighMultSPD_vsv0m", "HighMultV0_vsv0m"]
        labelsspd = ["kINT7_vsntracklets", "HighMultSPD_vsntracklets", "HighMultV0_vsntracklets"]
        cutonspd = [20, 30, 40, 50, 60]

        ctrigger = TCanvas('ctrigger', 'The Fit Canvas')
        ctrigger.SetCanvasSize(2100, 1000)
        ctrigger.Divide(2, 1)
        ctrigger.cd(1)
        leg = TLegend(.5, .65, .7, .85)
        leg.SetBorderSize(0)
        leg.SetFillColor(0)
        leg.SetFillStyle(0)
        leg.SetTextFont(42)
        leg.SetTextSize(0.035)
        for i, lab in enumerate(labelsv0):
            heff = filedata.Get("hnum%s" % lab)
            hden = filedata.Get("hden%s" % lab)
            heff.SetLineColor(i+1)
            heff.Divide(heff, hden, 1.0, 1.0, "B")
            heff.SetMaximum(2.)
            heff.GetXaxis().SetTitle("offline V0M")
            heff.SetMinimum(0.)
            heff.GetYaxis().SetTitle("trigger efficiency")
            heff.Draw("epsame")
            leg.AddEntry(heff, labelsv0[i], "LEP")
        leg.Draw()

        ctrigger.cd(2)
        lega = TLegend(.5, .65, .7, .85)
        lega.SetBorderSize(0)
        lega.SetFillColor(0)
        lega.SetFillStyle(0)
        lega.SetTextFont(42)
        lega.SetTextSize(0.035)
        for i, lab in enumerate(labelsspd):
            heff = filedata.Get("hnum%s" % lab)
            hden = filedata.Get("hden%s" % lab)
            heff.SetLineColor(i+1)
            heff.Divide(heff, hden, 1.0, 1.0, "B")
            heff.GetXaxis().SetTitle("offline SPD mul")
            heff.GetYaxis().SetTitle("trigger efficiency")
            heff.SetMinimum(0.)
            heff.SetMaximum(2.)
            heff.Draw("epsame")
            lega.AddEntry(heff, labelsspd[i], "LEP")
        lega.Draw()
        ctrigger.SaveAs("ctrigger.pdf")

        ccutstudy = TCanvas('ccutstudy', 'The Fit Canvas')
        ccutstudy.SetCanvasSize(2200, 1000)
        ccutstudy.Divide(2, 1)
        ccutstudy.cd(1)
        legc = TLegend(.5, .65, .7, .85)
        legc.SetBorderSize(0)
        legc.SetFillColor(0)
        legc.SetFillStyle(0)
        legc.SetTextFont(42)
        legc.SetTextSize(0.035)
        for i, lab in enumerate(cutonspd):
            hdenv0mdata = filedata.Get("hdenv0m")
            heffdata = filedata.Get("hnumv0mspd%d" % lab)
            heffdata.SetLineColor(i+1)
            heffdata.Divide(heffdata, hdenv0mdata, 1.0, 1.0, "B")
            heffdata.SetMaximum(2.)
            heffdata.GetXaxis().SetTitle("offline V0M (data)")
            heffdata.GetYaxis().SetTitle("pseudo efficiency")
            heffdata.Draw("epsame")
            legc.AddEntry(heffdata, "SPD mult >=%d" % lab, "LEP")
            legc.Draw()
        ccutstudy.cd(2)
        for i, lab in enumerate(cutonspd):
            hdenv0mmc = filemc.Get("hdenv0m")
            heffmc = filemc.Get("hnumv0mspd%d" % lab)
            heffmc.SetLineColor(i+1)
            heffmc.Divide(heffmc, hdenv0mmc, 1.0, 1.0, "B")
            heffmc.SetMaximum(2.)
            heffmc.GetXaxis().SetTitle("offline V0M (mc)")
            heffmc.GetYaxis().SetTitle("pseudo efficiency")
            heffmc.Draw("epsame")
            legc.Draw()
        ccutstudy.SaveAs("ccutstudy.pdf")
