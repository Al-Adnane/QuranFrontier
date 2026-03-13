/**
 * Ethical Governance API Endpoint
 * 
 * Provides access to Islamic AI ethics evaluation and governance reports
 * Based on: MDPI Religions 2025, Vol. 16, Page 796
 * "Artificial Intelligence and the Islamic Theology of Technology: 
 *  From 'Means' to 'Meanings' and from 'Minds' to 'Hearts'"
 * 
 * Public-Planet Partnerships Integration
 */

import { NextRequest, NextResponse } from 'next/server';
import {
  generateEthicalVerdict,
  generateGovernanceReport,
  integrateEthicalAnalysis,
  ETHICAL_PRINCIPLES,
  MAQASID_AL_SHARIAH,
  type EthicalVerdict,
  type EthicalGovernanceReport
} from '@/lib/security/islamic-ethics';

// ============================================================================
// TYPES
// ============================================================================

interface EthicsEvaluationRequest {
  action: string;
  stakeholders: string[];
  impacts: Record<string, number>;
  potentialHarms: string[];
  potentialBenefits: string[];
  harmPathways: string[];
  actor: string;
  declaredIntent?: string;
  requiresIjtihad?: boolean;
  ecologicalContext?: {
    bioSource?: string;
    partnershipModel?: string;
    regeneratePotential?: number;
  };
}

interface DetectionEthicsRequest {
  verdict: 'authentic' | 'deepfake' | 'manipulated' | 'uncertain';
  confidence: number;
  contentId: string;
  source: string;
  purpose: string;
  affectedParties: string[];
}

// ============================================================================
// GET HANDLER - System Status
// ============================================================================

export async function GET(request: NextRequest) {
  const { searchParams } = new URL(request.url);
  const action = searchParams.get('action');

  // If specific action requested, return principle info
  if (action) {
    const principle = ETHICAL_PRINCIPLES.find(p => p.id === action);
    if (principle) {
      return NextResponse.json({
        principle,
        maqasid: MAQASID_AL_SHARIAH
      });
    }
  }

  // Default: return system status
  return NextResponse.json({
    module: 'Islamic AI Ethics Governance',
    version: '2.1.0',
    description: 'Faith-aligned ethical principles for AI governance based on Islamic theology of technology',
    source: 'MDPI Religions 2025, Vol. 16, Page 796',
    principles: ETHICAL_PRINCIPLES.map(p => ({
      id: p.id,
      name: p.name,
      arabicName: p.arabicName,
      weight: p.weight
    })),
    maqasidAlShariah: Object.entries(MAQASID_AL_SHARIAH).map(([, value]) => ({
      id: value.id,
      name: value.name,
      weight: value.weight,
      description: value.description
    })),
    capabilities: {
      niyyahAssessment: 'Intentionality and moral clarity evaluation',
      maslahahEvaluation: 'Public interest (Daruriyyat, Hajjiyyat, Tahsiniyyat) analysis',
      saddAlDharai: 'Blocking means to harm assessment',
      ijtihad: 'Independent reasoning for novel situations',
      qalbAssessment: 'Heart (cognitive, moral, spiritual center) evaluation',
      governanceReport: 'Comprehensive ethical governance reporting',
      pppIntegration: 'Public-Planet Partnerships ecological governance'
    },
    endpoints: {
      'GET /api/ethics': 'System status and principles',
      'POST /api/ethics': 'Full ethical evaluation',
      'PUT /api/ethics': 'Detection-specific ethics integration'
    }
  });
}

// ============================================================================
// POST HANDLER - Full Ethical Evaluation
// ============================================================================

export async function POST(request: NextRequest) {
  try {
    const body: EthicsEvaluationRequest = await request.json();

    // Validate required fields
    if (!body.action || !body.stakeholders || !body.actor) {
      return NextResponse.json({
        error: 'Missing required fields: action, stakeholders, actor'
      }, { status: 400 });
    }

    // Convert impacts record to Map
    const impactsMap = new Map(Object.entries(body.impacts));

    // Generate ethical verdict
    const verdict: EthicalVerdict = generateEthicalVerdict(body.action, {
      stakeholders: body.stakeholders,
      impacts: impactsMap,
      potentialHarms: body.potentialHarms || [],
      potentialBenefits: body.potentialBenefits || [],
      harmPathways: body.harmPathways || [],
      actor: body.actor,
      declaredIntent: body.declaredIntent,
      requiresIjtihad: body.requiresIjtihad
    });

    // Generate governance report if content ID provided
    let governanceReport: EthicalGovernanceReport | null = null;
    if (body.ecologicalContext) {
      governanceReport = generateGovernanceReport(
        `ethics_${Date.now()}`,
        body.action,
        {
          ...body,
          impacts: impactsMap,
          ecologicalContext: body.ecologicalContext
        }
      );
    }

    // Build response
    const response = {
      timestamp: Date.now(),
      verdict: {
        permitted: verdict.permitted,
        ethicalScore: verdict.ethicalScore,
        ethicalScorePercent: `${(verdict.ethicalScore * 100).toFixed(1)}%`,
        conditions: verdict.conditions,
        recommendations: verdict.recommendations,
        warnings: verdict.warnings
      },
      principleAnalysis: {
        niyyah: {
          intent: verdict.principleAnalysis.niyyah.intent,
          moralClarity: verdict.principleAnalysis.niyyah.moralClarity,
          transparency: verdict.principleAnalysis.niyyah.transparency,
          accountabilityScore: verdict.principleAnalysis.niyyah.accountabilityScore,
          reasoning: verdict.principleAnalysis.niyyah.reasoning
        },
        maslahah: {
          overallScore: verdict.principleAnalysis.maslahah.overallScore,
          overallScorePercent: `${((verdict.principleAnalysis.maslahah.overallScore + 1) / 2 * 100).toFixed(1)}%`,
          categories: {
            essential: verdict.principleAnalysis.maslahah.categories.essential,
            complementary: verdict.principleAnalysis.maslahah.categories.complementary,
            embellishment: verdict.principleAnalysis.maslahah.categories.embellishment
          },
          reasoning: verdict.principleAnalysis.maslahah.reasoning
        },
        saddAlDharai: {
          harmPotential: verdict.principleAnalysis.saddAlDharai.harmPotential,
          riskLevel: verdict.principleAnalysis.saddAlDharai.riskLevel,
          blockingMechanisms: verdict.principleAnalysis.saddAlDharai.blockingMechanisms,
          preventiveMeasures: verdict.principleAnalysis.saddAlDharai.preventiveMeasures
        },
        qalb: {
          spiritualCenter: verdict.principleAnalysis.qalb.spiritualCenter,
          cognitiveAlignment: verdict.principleAnalysis.qalb.cognitiveAlignment,
          emotionalIntelligence: verdict.principleAnalysis.qalb.emotionalIntelligence,
          moralConviction: verdict.principleAnalysis.qalb.moralConviction,
          purification: verdict.principleAnalysis.qalb.purification
        }
      },
      ijtihad: verdict.ijtihad ? {
        situation: verdict.ijtihad.situation,
        primarySources: verdict.ijtihad.primarySources,
        secondarySources: verdict.ijtihad.secondarySources,
        conclusion: verdict.ijtihad.conclusion,
        confidence: verdict.ijtihad.confidence
      } : null,
      governanceReport: governanceReport ? {
        complianceStatus: governanceReport.complianceStatus,
        accountabilityChain: governanceReport.accountabilityChain,
        ecologicalImpact: governanceReport.ecologicalImpact
      } : null,
      islamicPrinciples: {
        maqasid: MAQASID_AL_SHARIAH,
        appliedPrinciples: ETHICAL_PRINCIPLES.filter(p => 
          p.applicationScope.includes('detection') || 
          p.applicationScope.includes('governance')
        )
      }
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Ethics evaluation error:', error);
    return NextResponse.json({
      error: 'Internal server error during ethics evaluation',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}

// ============================================================================
// PUT HANDLER - Detection-Specific Ethics Integration
// ============================================================================

export async function PUT(request: NextRequest) {
  try {
    const body: DetectionEthicsRequest = await request.json();

    // Validate required fields
    if (!body.verdict || body.confidence === undefined || !body.contentId) {
      return NextResponse.json({
        error: 'Missing required fields: verdict, confidence, contentId'
      }, { status: 400 });
    }

    // Integrate ethics with detection result
    const ethicsResult = integrateEthicalAnalysis(
      {
        verdict: body.verdict,
        confidence: body.confidence,
        contentId: body.contentId
      },
      {
        source: body.source || 'unknown',
        purpose: body.purpose || 'deepfake_detection',
        affectedParties: body.affectedParties || []
      }
    );

    // Generate full governance report
    const governanceReport = generateGovernanceReport(
      body.contentId,
      `Content analysis: ${body.verdict}`,
      {
        stakeholders: ['content_creator', 'viewer', 'platform', 'society', ...body.affectedParties],
        impacts: new Map([
          ['content_creator', body.verdict === 'deepfake' ? -0.3 : 0.2],
          ['viewer', body.verdict === 'deepfake' ? 0.8 : 0.5],
          ['platform', 0.5],
          ['society', body.verdict === 'deepfake' ? 0.6 : 0.3]
        ]),
        potentialHarms: body.verdict === 'deepfake' 
          ? ['misinformation spread', 'reputation damage', 'trust erosion']
          : ['false positive risk'],
        potentialBenefits: ['truth verification', 'user protection', 'platform integrity'],
        harmPathways: ['unverified sharing', 'context removal'],
        actor: 'Kasbah Detection System',
        declaredIntent: `Verify content authenticity (${body.purpose})`,
        ecologicalContext: {
          partnershipModel: 'Truth Preservation Partnership',
          regeneratePotential: 0.7
        }
      }
    );

    const response = {
      contentId: body.contentId,
      detectionVerdict: body.verdict,
      detectionConfidence: body.confidence,
      ethicsIntegration: {
        enhancedVerdict: ethicsResult.enhancedVerdict,
        ethicalConditions: ethicsResult.ethicalConditions,
        accountabilityNote: ethicsResult.accountabilityNote
      },
      governanceReport: {
        permitted: governanceReport.verdict.permitted,
        ethicalScore: governanceReport.verdict.ethicalScore,
        complianceStatus: governanceReport.complianceStatus,
        accountabilityChain: governanceReport.accountabilityChain,
        ecologicalImpact: governanceReport.ecologicalImpact
      },
      recommendations: governanceReport.verdict.recommendations,
      warnings: governanceReport.verdict.warnings,
      islamicContext: {
        principles: ETHICAL_PRINCIPLES.filter(p => 
          p.applicationScope.includes('detection')
        ),
        quranicReferences: [
          "Qur'an 49:6 - Verify information before acting",
          "Qur'an 17:36 - Do not pursue what you have no knowledge of",
          "Qur'an 2:195 - Do not contribute to your own destruction"
        ]
      },
      timestamp: Date.now()
    };

    return NextResponse.json(response);
  } catch (error) {
    console.error('Detection ethics integration error:', error);
    return NextResponse.json({
      error: 'Internal server error during ethics integration',
      details: error instanceof Error ? error.message : 'Unknown error'
    }, { status: 500 });
  }
}
